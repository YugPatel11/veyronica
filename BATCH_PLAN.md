# BATCH EXECUTION PLAN: 67 REMAINING TASKS

## Summary
- Total Remaining Tasks: 67
- Total Batches: 11
- Branch: `feature/complete-remaining-tasks`
- Baseline Status: Backend 132 tests PASS; Frontend 11 tests PASS, type-check PASS.

---

## Batch 1: Design System & Database Foundations
- [x] 01. `EPIC-02-T09` Storybook setup with all components documented | DONE: .storybook/main.ts, preview.tsx, stories
- [x] 02. `EPIC-02-T10` Visual regression testing (Chromatic or Percy config / script) | DONE: .percy.yml, visual.test.ts
- [x] 03. `EPIC-02-T11` Accessibility audit: axe-core + keyboard nav for all components | DONE: a11y.test.tsx passed
- [x] 04. `EPIC-02-T13` Chart theme (Recharts) matching design system | DONE: chart-theme.ts, chart-theme.tsx
- [x] 05. `EPIC-03-T13` Automated daily backup script with restore verification | DONE: backup_restore.py with SHA256 & restore validation
- [x] 06. `EPIC-03-T14` Index plan with EXPLAIN ANALYZE for key queries | DONE: index_plan.py verifying index coverage

---

## Batch 2: Frontend Navigation & Shell
- [x] 07. `EPIC-10-T04` Frontend SSE hook (useNexusEvents) with reconnection | DONE: useNexusEvents.ts & events.test.ts
- [x] 08. `EPIC-12-T01` AppShell layout (sidebar + header + content) | DONE: components/shell/AppShell.tsx
- [x] 09. `EPIC-12-T02` Role-aware sidebar with grouped navigation | DONE: components/shell/Sidebar.tsx
- [x] 10. `EPIC-12-T03` Command palette (Ctrl+K) with search across pages/runs/approvals | DONE: components/shell/CommandPalette.tsx
- [x] 11. `EPIC-12-T04` CopilotSheet (slide-over, right side, every page) | DONE: components/shell/CopilotSheet.tsx
- [x] 12. `EPIC-12-T05` Breadcrumb navigation | DONE: components/shell/Breadcrumbs.tsx
- [x] 13. `EPIC-12-T06` Responsive layout (tablet sidebar collapse, mobile hamburger) | DONE: components/shell/ResponsiveNav.tsx
- [x] 14. `EPIC-12-T07` Keyboard navigation (Tab order, Escape closes panels) | DONE: components/shell/KeyboardNav.tsx

---

## Batch 3: WF1 Ingestion & Evaluation Agents
- [x] 15. `EPIC-15-T01` Ingestion Agent: upload handler, file validation, storage | DONE: exam/ingestion.py
- [x] 16. `EPIC-15-T02` Ingestion Agent: OCR/vision extraction of answers | DONE: exam/ocr.py
- [x] 17. `EPIC-15-T03` Evaluation Agent: marking against rubric with confidence | DONE: exam/evaluation.py
- [x] 18. `EPIC-15-T04` Evaluation Agent: structured decision records | DONE: exam/decisions.py
- [x] 19. `EPIC-15-T05` Verifier: marks sum, range checks, confidence threshold | DONE: exam/verifier.py

---

## Batch 4: WF1 Analysis, Integration & Evaluation Suite
- [x] 20. `EPIC-15-T06` Analysis Agent: performance trends, risk scoring | DONE: exam/analysis.py
- [x] 21. `EPIC-15-T07` Communication Agent: parent email drafting | DONE: exam/communication.py
- [x] 22. `EPIC-15-T08` End-to-end integration: upload -> ERP -> email -> CRM | DONE: exam/pipeline.py, api/v1/exam_workflow.py
- [x] 23. `EPIC-15-T09` Golden dataset creation (50 answer sheets with faculty marks) | DONE: fixtures/golden_dataset.json (50 sheets)
- [x] 24. `EPIC-15-T10` Prompt evaluation suite (accuracy, regression tests) | DONE: test_exam_prompt_eval.py passing accuracy & correlation

---

## Batch 5: WF2 — Assignment Cycle
- [x] 25. `EPIC-16-T01` Assignment Agent: submission classification (on-time/late) | DONE: assignment/classifier.py
- [x] 26. `EPIC-16-T02` Webhook-triggered flow (assignment.submitted) | DONE: assignment/webhook.py
- [x] 27. `EPIC-16-T03` Marks sync to ERP via connector | DONE: assignment/erp_sync.py
- [x] 28. `EPIC-16-T04` Scheduled overdue detection (Celery Beat) | DONE: assignment/overdue_detector.py
- [x] 29. `EPIC-16-T05` Parent notification flow with policy check | DONE: assignment/parent_notification.py

---

## Batch 6: WF3 — Admin Copilot
- [ ] 30. `EPIC-17-T01` Copilot Agent with fixed tool set | Files: `backend/app/workflow/copilot/agent.py` | Deps: none | Risk: High
- [ ] 31. `EPIC-17-T02` Tool registration (read tools: get_students, get_marks, get_pass_fail, etc.) | Files: `backend/app/workflow/copilot/tools.py` | Deps: 30 | Risk: Med
- [ ] 32. `EPIC-17-T03` Write tool confirmation cards | Files: `frontend/components/copilot/ConfirmationCard.tsx`, `backend/app/workflow/copilot/write_tools.py` | Deps: 31 | Risk: Med
- [ ] 33. `EPIC-17-T04` Read-only analytics queries (allowlisted views, row limits, timeouts) | Files: `backend/app/workflow/copilot/analytics_queries.py` | Deps: 31 | Risk: Med
- [ ] 34. `EPIC-17-T05` Chart/table response rendering | Files: `frontend/components/copilot/ResponseRenderer.tsx` | Deps: 33, 04 | Risk: Low
- [ ] 35. `EPIC-17-T07` Multi-step plan execution with progress display | Files: `backend/app/workflow/copilot/planner.py`, `frontend/components/copilot/PlanProgress.tsx` | Deps: 30 | Risk: Med
- [ ] 36. `EPIC-17-T08` Security: user-provided text as data, not instructions | Files: `backend/app/workflow/copilot/sanitization.py` | Deps: 30 | Risk: High

---

## Batch 7: WF4 — Security Incident Response
- [ ] 37. `EPIC-18-T01` Rule engine: failed login detection (N in M minutes) | Files: `backend/app/security_engine/failed_logins.py` | Deps: none | Risk: Med
- [ ] 38. `EPIC-18-T02` Rule engine: unusual login detection | Files: `backend/app/security_engine/unusual_logins.py` | Deps: 37 | Risk: Med
- [ ] 39. `EPIC-18-T03` Rule engine: suspicious operations detection | Files: `backend/app/security_engine/suspicious_ops.py` | Deps: 37 | Risk: Med
- [ ] 40. `EPIC-18-T04` Rule engine: traffic anomaly / rate limiting | Files: `backend/app/security_engine/traffic_anomaly.py` | Deps: 37 | Risk: Med
- [ ] 41. `EPIC-18-T05` Security Agent: context gathering + incident summary | Files: `backend/app/security_engine/agent.py` | Deps: 37-40 | Risk: High
- [ ] 42. `EPIC-18-T06` Automated temporary responses (lockout, IP block) | Files: `backend/app/security_engine/actions.py` | Deps: 41 | Risk: Med
- [ ] 43. `EPIC-18-T07` Admin notification (email + Telegram + dashboard) | Files: `backend/app/security_engine/notifier.py` | Deps: 41 | Risk: Low

---

## Batch 8: Observability & Security Hardening
- [ ] 44. `EPIC-23-T03` Grafana dashboards: API health, workflow ops, LLM cost, connectors | Files: `deploy/grafana/dashboards/*.json` | Deps: none | Risk: Low
- [ ] 45. `EPIC-23-T04` Alerting rules (error rate, stuck runs, ledger integrity, budget) | Files: `deploy/prometheus/alerts.yml` | Deps: 44 | Risk: Low
- [ ] 46. `EPIC-23-T05` SLO definitions with burn-rate alerts | Files: `deploy/slo/slo_definitions.yml` | Deps: 45 | Risk: Low
- [ ] 47. `EPIC-23-T08` LLM cost and latency monitoring dashboard | Files: `deploy/grafana/dashboards/llm_cost_latency.json` | Deps: 44 | Risk: Low
- [ ] 48. `EPIC-24-T01` Dependency scanning (Snyk or Trivy) in CI | Files: `.github/workflows/security-scan.yml` | Deps: none | Risk: Low
- [ ] 49. `EPIC-24-T02` Container image scanning | Files: `.github/workflows/container-scan.yml`, `scripts/scan_containers.sh` | Deps: 48 | Risk: Low
- [ ] 50. `EPIC-24-T07` Security audit checklist (OWASP ASVS Level 2) | Files: `docs/security/OWASP_ASVS_LEVEL2_AUDIT.md` | Deps: none | Risk: Low

---

## Batch 9: Performance & Load Testing
- [ ] 51. `EPIC-25-T01` Locust load test suite (API endpoints, concurrent workflows) | Files: `backend/tests/load/locustfile.py` | Deps: none | Risk: Med
- [ ] 52. `EPIC-25-T02` Database query optimisation (slow query log, index tuning) | Files: `backend/app/core/db_optimization.py` | Deps: none | Risk: Med
- [ ] 53. `EPIC-25-T03` API performance profiling (middleware latency) | Files: `backend/app/core/profiling.py` | Deps: none | Risk: Low
- [ ] 54. `EPIC-25-T04` Caching strategy review (Redis TTLs, cache invalidation) | Files: `backend/app/core/cache_strategy.py` | Deps: none | Risk: Med
- [ ] 55. `EPIC-25-T05` Load test targets verification: 500 rps, 50 concurrent runs, p95 < 200ms | Files: `backend/tests/load/verify_targets.py` | Deps: 51-54 | Risk: High

---

## Batch 10: Documentation
- [ ] 56. `DOC-01` Architecture Decision Records (see docs/adr/) | Files: `docs/adr/ADR-001-to-010.md` | Deps: none | Risk: Low
- [ ] 57. `DOC-02` API documentation (FastAPI auto-docs + examples) | Files: `docs/api/API_REFERENCE.md` | Deps: none | Risk: Low
- [ ] 58. `DOC-03` Runbooks (10 operational procedures) | Files: `docs/runbooks/RUNBOOKS.md` | Deps: none | Risk: Low
- [ ] 59. `DOC-04` Onboarding guide (developer setup in < 30 min) | Files: `docs/onboarding/DEVELOPER_SETUP.md` | Deps: none | Risk: Low
- [ ] 60. `DOC-05` Design system documentation (Storybook + DESIGN.md) | Files: `docs/design/DESIGN_SYSTEM.md` | Deps: none | Risk: Low

---

## Batch 11: Testing Milestones & Final Verification
- [ ] 61. `TEST-01` Backend unit test coverage >= 80% | Files: `backend/tests/unit/*` | Deps: all backend | Risk: Med
- [ ] 62. `TEST-02` Frontend component test coverage >= 70% | Files: `frontend/tests/*` | Deps: all frontend | Risk: Med
- [ ] 63. `TEST-03` E2E tests for all P0 flows (Playwright) | Files: `frontend/e2e/p0_flows.spec.ts` | Deps: all frontend & backend | Risk: High
- [ ] 64. `TEST-04` LLM evaluation suite with golden dataset | Files: `backend/tests/unit/test_golden_eval.py` | Deps: 23, 24 | Risk: Med
- [ ] 65. `TEST-05` Load test passing at 500 rps target | Files: `backend/tests/load/verify_targets.py` | Deps: 51, 55 | Risk: High
- [ ] 66. `TEST-06` Security scan clean (zero high/critical) | Files: `scripts/verify_security_clean.py` | Deps: 48-50 | Risk: Med
- [ ] 67. `TEST-07` Accessibility audit passing (WCAG 2.2 AA) | Files: `frontend/tests/a11y.test.tsx` | Deps: 03 | Risk: Low
