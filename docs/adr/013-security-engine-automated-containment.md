# ADR-013: WF4 Autonomous Security Incident Response & Temporary Containment

## Status
Accepted (October 2026)

## Context
Educational institutions are frequent targets of brute-force attacks, credential stuffing, and data scraping. Manual security triage introduces delays that allow attackers to compromise accounts or exfiltrate grades.

## Decision
We implemented an autonomous security response engine (`app/security_engine/`):
1. **Rule Engine:** Analyzes failed logins (N in M minutes), unusual logins (impossible travel, new IP, off-hours), suspicious operations (mass export, 403 bursts), and traffic anomalies (spikes, high error rate).
2. **Autonomous Triage:** The Security Agent aggregates alerts, gathers user and IP context, computes incident severity (LOW, MEDIUM, HIGH, CRITICAL), and determines containment actions.
3. **Automated Containment:** For CRITICAL threats, the system autonomously applies temporary IP blocks (60m) and account lockouts (30m) via `SecurityActionHandler`.
4. **Multi-Channel Alerting & Audit:** Notifies admins across Email, Telegram, and In-App dashboard while writing a tamper-evident entry to the hash-chained Decision Ledger.

## Consequences
- **Pros:** Real-time containment within seconds; zero administrator intervention needed for urgent lockouts.
- **Cons:** Accidental lockouts on legitimate users if passwords are forgotten; mitigated by self-service MFA reset and admin unblock UI.

## Verification
- `backend/tests/unit/test_security_engine.py`
