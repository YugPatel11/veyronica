# ADR-003: LiteLLM for Provider-Agnostic LLM Access

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §12 specifies "provider-agnostic via a gateway (optionally LiteLLM)." NEXUS needs to route calls to different LLM providers based on tier (small/medium/strong), with fallback if a provider is down. The gateway must also support budget guards, caching, and usage logging.

## Decision

- Use **LiteLLM** as the provider abstraction layer inside the LLM Gateway.
- LiteLLM supports 100+ models across OpenAI, Google, Anthropic, Azure, and others with a unified API.
- The NEXUS LLM Gateway wraps LiteLLM with additional logic: tier routing, budget guard, PII pseudonymisation, schema validation, caching, and usage logging.
- LiteLLM is used as a library (imported directly), not as a proxy server, to avoid an extra network hop.

## Consequences

- Adding a new LLM provider requires only a config change (tier → model mapping), not code changes.
- LiteLLM's unified error handling simplifies retry and fallback logic.
- Dependency on LiteLLM — but it's well-maintained and the abstraction is thin enough to replace if needed.
- Provider-specific features (e.g., function calling, streaming) must be used through LiteLLM's abstraction, which may lag behind provider releases.
