# ADR-011: WF1 Exam Result Ingestion with Dual-Pass Verifier

## Status
Accepted (October 2026)

## Context
Grading student answer sheets with LLMs carries the risk of arithmetic hallucination, rubric drift, or low-confidence errors. University regulations mandate that no final mark is committed without verifiable arithmetic accuracy and faculty oversight for borderline or low-confidence scores.

## Decision
We implemented a dual-stage pipeline:
1. An **Evaluation Agent** (`app/workflow/exam/evaluation.py`) performs rubric concept matching and assigns raw sub-question marks with confidence scores and reasoning.
2. A deterministic **Verifier** (`app/workflow/exam/verifier.py`) checks arithmetic summation, maximum possible marks, rubric boundaries, and confidence thresholds (< 0.70 flags for human review).
3. If verification succeeds with high confidence, the system generates signed decision records (`app/workflow/exam/decisions.py`) with SHA-256 hashes before syncing to the ERP connector.

## Consequences
- **Pros:** 100% elimination of arithmetic hallucination; full audit trail for student grade disputes.
- **Cons:** Borderline answer sheets require faculty review in the Approval Inbox before ERP publishing.

## Verification
- `backend/tests/unit/test_exam_workflow_agents.py`
- `backend/tests/unit/test_exam_prompt_eval.py` (50 golden dataset answer sheets)
