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
- [ ] 07. `EPIC-10-T04` Frontend SSE hook (useNexusEvents) with reconnection | Files: `frontend/lib/useNexusEvents.ts` | Deps: none | Risk: Med
- [ ] 08. `EPIC-12-T01` AppShell layout (sidebar + header + content) | Files: `frontend/components/shell/AppShell.tsx`, `frontend/app/(dashboard)/layout.tsx` | Deps: none | Risk: Med
- [ ] 09. `EPIC-12-T02` Role-aware sidebar with grouped navigation | Files: `frontend/components/shell/Sidebar.tsx` | Deps: 08 | Risk: Low
- [ ] 10. `EPIC-12-T03` Command palette (Ctrl+K) with search across pages/runs/approvals | Files: `frontend/components/shell/CommandPalette.tsx` | Deps: 08 | Risk: Low
- [ ] 11. `EPIC-12-T04` CopilotSheet (slide-over, right side, every page) | Files: `frontend/components/shell/CopilotSheet.tsx` | Deps: 08 | Risk: Low
- [ ] 12. `EPIC-12-T05` Breadcrumb navigation | Files: `frontend/components/shell/Breadcrumbs.tsx` | Deps: 08 | Risk: Low
- [ ] 13. `EPIC-12-T06` Responsive layout (tablet sidebar collapse, mobile hamburger) | Files: `frontend/components/shell/ResponsiveNav.tsx` | Deps: 08, 09 | Risk: Low
- [ ] 14. `EPIC-12-T07` Keyboard navigation (Tab order, Escape closes panels) | Files: `frontend/components/shell/KeyboardNav.tsx` | Deps: 08, 10, 11 | Risk: Low

---

## Batch 3: WF1 Ingestion & Evaluation Agents
- [ ] 15. `EPIC-15-T01` Ingestion Agent: upload handler, file validation, storage | Files: `backend/app/workflow/exam/ingestion.py` | Deps: none | Risk: Med
- [ ] 16. `EPIC-15-T02` Ingestion Agent: OCR/vision extraction of answers | Files: `backend/app/workflow/exam/ocr.py` | Deps: 15 | Risk: Med
- [ ] 17. `EPIC-15-T03` Evaluation Agent: marking against rubric with confidence | Files: `backend/app/workflow/exam/evaluation.py` | Deps: 16 | Risk: High
- [ ] 18. `EPIC-15-T04` Evaluation Agent: structured decision records | Files: `backend/app/workflow/exam/decisions.py` | Deps: 17 | Risk: Med
- [ ] 19. `EPIC-15-T05` Verifier: marks sum, range checks, confidence threshold | Files: `backend/app/workflow/exam/verifier.py` | Deps: 18 | Risk: Med

---

## Batch 4: WF1 Analysis, Integration & Evaluation Suite
- [ ] 20. `EPIC-15-T06` Analysis Agent: performance trends, risk scoring | Files: `backend/app/workflow/exam/analysis.py` | Deps: 19 | Risk: Med
- [ ] 21. `EPIC-15-T07` Communication Agent: parent email drafting | Files: `backend/app/workflow/exam/communication.py` | Deps: 20 | Risk: Low
- [ ] 22. `EPIC-15-T08` End-to-end integration: upload -> ERP -> email -> CRM | Files: `backend/app/workflow/exam/pipeline.py`, `backend/app/api/v1/exam_workflow.py` | Deps: 15-21 | Risk: High
- [ ] 23. `EPIC-15-T09` Golden dataset creation (50 answer sheets with faculty marks) | Files: `backend/tests/fixtures/golden_dataset.json` | Deps: none | Risk: Low
- [ ] 24. `EPIC-15-T10` Prompt evaluation suite (accuracy, regression tests) | Files: `backend/tests/unit/test_exam_prompt_eval.py` | Deps: 23 | Risk: Med

---

## Batch 5: WF2 — Assignment Cycle
- [ ] 25. `EPIC-16-T01` Assignment Agent: submission classification (on-time/late) | Files: `backend/app/workflow/assignment/classifier.py` | Deps: none | Risk: Med
- [ ] 26. `EPIC-16-T02` Webhook-triggered flow (assignment.submitted) | Files: `backend/app/workflow/assignment/webhook.py` | Deps: 25 | Risk: Med
- [ ] 27. `EPIC-16-T03` Marks sync to ERP via connector | Files: `backend/app/workflow/assignment/erp_sync.py` | Deps: 25 | Risk: Med
- [ ] 28. `EPIC-16-T04` Scheduled overdue detection (Celery Beat) | Files: `backend/app/workflow/assignment/overdue_detector.py` | Deps: none | Risk: Med
- [ ] 29. `EPIC-16-T05` Parent notification flow with policy check | Files: `backend/app/workflow/assignment/parent_notification.py` | Deps: 28 | Risk: Low

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
