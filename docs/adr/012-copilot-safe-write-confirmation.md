# ADR-012: WF3 Admin Copilot Read-Only Analytics & Confirmation Cards

## Status
Accepted (October 2026)

## Context
The Admin Copilot has access to sensitive student records and academic operations. If allowed to execute direct SQL mutations or state modifications autonomously via conversational prompts, prompt injection or user error could cause unintended data modification or exfiltration.

## Decision
1. **Strict Read/Write Separation:**
   - Analytics queries run through allowlisted views (`app/workflow/copilot/analytics_queries.py`) with strict row limits (max 500) and forbidden keyword validation (`INSERT`, `UPDATE`, `DELETE`, `DROP`).
2. **Safe Write Tools with Confirmation Cards:**
   - Any state mutation (e.g., student roster updates, schedule changes) emits a pending action with a cryptographically signed one-time confirmation token (`cf_*`) valid for 5 minutes (`app/workflow/copilot/write_tools.py`).
   - The UI renders an interactive `ConfirmationCard.tsx` showing the diff, affected entities, and risk level. The action only executes when the administrator explicitly clicks "Confirm Action".
3. **Prompt Injection Guardrails:**
   - All user input is sanitized and wrapped in non-executable `<user_data>` XML tags (`app/workflow/copilot/sanitization.py`).

## Consequences
- **Pros:** Impossible for a prompt injection to autonomously alter the database; transparent human approval for changes.
- **Cons:** Write actions require two round trips (propose action -> confirm card).

## Verification
- `backend/tests/unit/test_copilot_workflow.py`
- `frontend/tests/copilot.test.tsx`
