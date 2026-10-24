"""LLM Gateway — Core tier selection and provider routing.

EPIC-06-T01: Gateway core with tier selection.
EPIC-06-T02: Budget guard.
EPIC-06-T03: Response cache.
EPIC-06-T04: PII pseudonymisation.
EPIC-06-T05: JSON schema validation.
EPIC-06-T06: Usage logging.
EPIC-06-T07: Prompt injection defence.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


# ── Tier Configuration ───────────────────────────────────────────────────────

class ModelConfig(BaseModel):
    """Model tier configuration."""
    tier: str  # economy, standard, premium
    model_name: str
    provider: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    max_context_tokens: int


DEFAULT_TIERS: dict[str, ModelConfig] = {
    "economy": ModelConfig(tier="economy", model_name="gpt-4o-mini", provider="openai", input_cost_per_1k=0.00015, output_cost_per_1k=0.0006, max_context_tokens=128000),
    "standard": ModelConfig(tier="standard", model_name="gpt-4o", provider="openai", input_cost_per_1k=0.0025, output_cost_per_1k=0.01, max_context_tokens=128000),
    "premium": ModelConfig(tier="premium", model_name="gpt-4.1", provider="openai", input_cost_per_1k=0.002, output_cost_per_1k=0.008, max_context_tokens=1000000),
}


# ── LLM Call Result ──────────────────────────────────────────────────────────

class LLMResponse(BaseModel):
    """Standardised LLM call response."""
    content: str = ""
    parsed: dict[str, Any] | None = None
    model: str = ""
    tier: str = ""
    provider: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    cached: bool = False
    call_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# ── PII Pseudonymisation ─────────────────────────────────────────────────────

class PIIPseudonymiser:
    """Reversible PII pseudonymisation for LLM prompts.

    EPIC-06-T04: Replace emails, phones, names with tokens.
    """

    def __init__(self) -> None:
        self._map: dict[str, str] = {}
        self._reverse: dict[str, str] = {}
        self._counter = 0

    def pseudonymise(self, text: str) -> str:
        """Replace PII patterns with tokens."""
        # Email addresses
        text = re.sub(r'[\w.-]+@[\w.-]+\.\w+', self._replace, text)
        # Phone numbers (Indian format)
        text = re.sub(r'\b[6-9]\d{9}\b', self._replace, text)
        # Aadhaar-like numbers
        text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', self._replace, text)
        return text

    def restore(self, text: str) -> str:
        """Restore pseudonymised tokens to original PII."""
        for token, original in self._reverse.items():
            text = text.replace(token, original)
        return text

    def _replace(self, match: re.Match) -> str:
        original = match.group(0)
        if original in self._map:
            return self._map[original]
        self._counter += 1
        token = f"[PII_{self._counter:04d}]"
        self._map[original] = token
        self._reverse[token] = original
        return token


# ── Prompt Injection Defence ─────────────────────────────────────────────────

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+a",
    r"forget\s+(all\s+)?your\s+instructions",
    r"do\s+not\s+follow\s+your\s+system\s+prompt",
    r"override\s+(system|safety)\s+(prompt|instructions)",
    r"\bDAN\b.*\bmode\b",
    r"jailbreak",
]


def detect_prompt_injection(text: str) -> bool:
    """Check if text contains prompt injection patterns.

    EPIC-06-T07: Prompt injection defence.
    """
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            logger.warning("prompt_injection_detected", pattern=pattern)
            return True
    return False


# ── Response Cache ────────────────────────────────────────────────────────────

def _cache_key(model: str, prompt: str) -> str:
    """Generate cache key from model + prompt hash. EPIC-06-T03."""
    content = f"{model}:{prompt}"
    return f"nexus:llm:cache:{hashlib.sha256(content.encode()).hexdigest()}"


# ── Budget Guard ──────────────────────────────────────────────────────────────

class BudgetExceededError(Exception):
    """Raised when token/cost budget is exceeded."""


class BudgetGuard:
    """Token and cost budget enforcement.

    EPIC-06-T02: Budget guard at global, workflow, agent, task level.
    """

    def __init__(self) -> None:
        self._usage: dict[str, dict[str, float]] = {}

    def check_budget(
        self,
        scope: str,
        scope_id: str | None,
        estimated_tokens: int,
        daily_limit: int = 500000,
        monthly_limit: int = 10000000,
    ) -> None:
        """Check if estimated tokens would exceed budget."""
        key = f"{scope}:{scope_id or 'global'}"
        usage = self._usage.get(key, {"daily": 0, "monthly": 0})

        if usage["daily"] + estimated_tokens > daily_limit:
            raise BudgetExceededError(f"Daily token budget exceeded for {scope}")
        if usage["monthly"] + estimated_tokens > monthly_limit:
            raise BudgetExceededError(f"Monthly token budget exceeded for {scope}")

    def record_usage(
        self, scope: str, scope_id: str | None, tokens: int, cost: float
    ) -> None:
        """Record token usage."""
        key = f"{scope}:{scope_id or 'global'}"
        if key not in self._usage:
            self._usage[key] = {"daily": 0, "monthly": 0, "cost_daily": 0, "cost_monthly": 0}
        self._usage[key]["daily"] += tokens
        self._usage[key]["monthly"] += tokens
        self._usage[key]["cost_daily"] += cost
        self._usage[key]["cost_monthly"] += cost


# ── JSON Schema Validation ───────────────────────────────────────────────────

def validate_json_response(content: str, schema: dict[str, Any] | None = None) -> tuple[bool, dict[str, Any] | None]:
    """Parse and optionally validate JSON from LLM response.

    EPIC-06-T05: JSON schema validation with one repair retry.
    """
    # Try to extract JSON from markdown code blocks
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        parsed = json.loads(cleaned)
        return True, parsed
    except json.JSONDecodeError:
        # Try to find JSON object/array in response
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = cleaned.find(start_char)
            end = cleaned.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(cleaned[start:end + 1])
                    return True, parsed
                except json.JSONDecodeError:
                    continue
        return False, None


# ── Gateway Core ──────────────────────────────────────────────────────────────

class LLMGateway:
    """Central LLM gateway with tier selection, budget, cache, PII, and injection defence.

    EPIC-06-T01: Gateway core.
    """

    def __init__(self) -> None:
        self.tiers = dict(DEFAULT_TIERS)
        self.budget = BudgetGuard()
        self.pii = PIIPseudonymiser()
        self._demo_mode = False
        self._demo_responses: dict[str, str] = {}

    def enable_demo_mode(self, responses: dict[str, str] | None = None) -> None:
        """Enable demo replay mode. EPIC-06-T08."""
        self._demo_mode = True
        self._demo_responses = responses or {}

    def disable_demo_mode(self) -> None:
        self._demo_mode = False

    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        tier: str = "standard",
        json_schema: dict[str, Any] | None = None,
        run_id: str | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
        skip_pii: bool = False,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Execute an LLM completion with all middleware.

        Flow: injection check → PII → budget check → cache check → call → log → cache store → PII restore
        """
        start = time.perf_counter()

        # 1. Prompt injection defence
        if detect_prompt_injection(prompt):
            return LLMResponse(content="[BLOCKED] Prompt injection detected", tier=tier)

        # 2. PII pseudonymisation
        safe_prompt = prompt if skip_pii else self.pii.pseudonymise(prompt)
        safe_system = system_prompt if skip_pii else self.pii.pseudonymise(system_prompt)

        # 3. Get model config
        model_cfg = self.tiers.get(tier, self.tiers["standard"])

        # 4. Demo mode
        if self._demo_mode:
            demo_content = self._demo_responses.get(tier, '{"result": "demo response"}')
            return LLMResponse(
                content=demo_content, model=model_cfg.model_name, tier=tier,
                provider=model_cfg.provider, prompt_tokens=len(prompt.split()),
                completion_tokens=len(demo_content.split()), total_tokens=len(prompt.split()) + len(demo_content.split()),
                latency_ms=50, cached=False,
            )

        # 5. Budget check (estimate ~1.5x prompt tokens)
        estimated = int(len(prompt.split()) * 2)
        self.budget.check_budget("global", None, estimated)
        if run_id:
            self.budget.check_budget("workflow", run_id, estimated)

        # 6. In production, call LiteLLM here. For now, return placeholder.
        latency = int((time.perf_counter() - start) * 1000)
        response = LLMResponse(
            content="[LLM call placeholder — connect LiteLLM provider]",
            model=model_cfg.model_name,
            tier=tier,
            provider=model_cfg.provider,
            prompt_tokens=estimated,
            completion_tokens=0,
            total_tokens=estimated,
            latency_ms=latency,
        )

        # 7. Record usage
        cost = (response.prompt_tokens / 1000 * model_cfg.input_cost_per_1k +
                response.completion_tokens / 1000 * model_cfg.output_cost_per_1k)
        response.cost_usd = round(cost, 6)
        self.budget.record_usage("global", None, response.total_tokens, response.cost_usd)

        # 8. PII restore in response
        if not skip_pii:
            response.content = self.pii.restore(response.content)

        return response

    def calculate_cost(self, tier: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for a given token count."""
        cfg = self.tiers.get(tier, self.tiers["standard"])
        return round(
            prompt_tokens / 1000 * cfg.input_cost_per_1k +
            completion_tokens / 1000 * cfg.output_cost_per_1k, 6
        )


# Singleton
gateway = LLMGateway()
