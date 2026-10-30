# Nexus Operational Runbooks (SRE & Operations)

This document contains step-by-step Standard Operating Procedures (SOPs) for responding to alerts, mitigating service degradation, and restoring system integrity.

---

## Index of Operational Procedures

- [RB-01: High HTTP 5xx Error Rate Response](#rb-01-high-http-5xx-error-rate-response)
- [RB-02: Stuck Workflow Run Remediation & Task Recovery](#rb-02-stuck-workflow-run-remediation--task-recovery)
- [RB-03: Cryptographic Decision Ledger Hash Mismatch Forensics](#rb-03-cryptographic-decision-ledger-hash-mismatch-forensics)
- [RB-04: LLM Budget Quota Exhaustion & Fallback Downgrade](#rb-04-llm-budget-quota-exhaustion--fallback-downgrade)
- [RB-05: External Connector Circuit Breaker Recovery](#rb-05-external-connector-circuit-breaker-recovery)
- [RB-06: Database Failover, Restore & Disaster Recovery](#rb-06-database-failover-restore--disaster-recovery)
- [RB-07: Brute Force & Credential Stuffing Emergency Lockout](#rb-07-brute-force--credential-stuffing-emergency-lockout)
- [RB-08: Redis Connection Outage & Token Blacklist Fallback](#rb-08-redis-connection-outage--token-blacklist-fallback)
- [RB-09: Production Secrets & Key Rotation](#rb-09-production-secrets--key-rotation)
- [RB-10: Celery Worker Deadlock & Queue Congestion Recovery](#rb-10-celery-worker-deadlock--queue-congestion-recovery)

---

## RB-01: High HTTP 5xx Error Rate Response

**Trigger Alert:** `HighHttpErrorRate` (5xx > 1.0% over 5 minutes)  
**Severity:** Critical  

### Immediate Actions:
1. **Check API Pod Health:**
   ```bash
   curl -s http://localhost:8000/health | jq .
   ```
2. **Inspect Error Logs for Correlation ID:**
   ```bash
   docker logs nexus-api --tail 100 | grep '"level":"error"'
   ```
3. **Check Database Connection Pool:**
   - Look for `QueuePool limit exceeded` or connection exhaustion.
   - If exhausted, scale `POSTGRES_POOL_SIZE` or restart FastAPI workers:
   ```bash
   docker restart nexus-api
   ```
4. **Verify Rollback Need:**
   - If error surge started immediately after deployment, roll back to previous image tag.

---

## RB-02: Stuck Workflow Run Remediation & Task Recovery

**Trigger Alert:** `StuckWorkflowRun` (Execution in `running` state > 15 minutes)  
**Severity:** Critical  

### Immediate Actions:
1. **Locate the Stalled Run ID:**
   ```bash
   curl -s http://localhost:8000/api/v1/workflows?status=running | jq '.runs[] | select(.duration_seconds > 900)'
   ```
2. **Inspect Worker Task Logs:**
   ```bash
   docker logs nexus-celery-worker --tail 200 | grep "<RUN_ID>"
   ```
3. **Terminate or Re-queue Run:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/workflows/<RUN_ID>/cancel
   ```
4. **If Worker is Deadlocked:**
   ```bash
   docker restart nexus-celery-worker
   ```

---

## RB-03: Cryptographic Decision Ledger Hash Mismatch Forensics

**Trigger Alert:** `LedgerIntegrityMismatch`  
**Severity:** Critical  

### Immediate Actions:
1. **Trigger Manual Chain Verification:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/audit/verify | jq .
   ```
2. **Identify Broken Sequence:**
   - The response provides `last_verified_sequence`. Entry `N+1` contains the discrepancy.
3. **Isolate Suspected Database Row:**
   - Query the `audit_ledger` table at sequence `N+1`. Check `updated_at` vs `created_at` timestamp.
4. **Initiate Security Review:**
   - Export cryptographic proof and report to CISO. Lock affected database tables to read-only mode during investigation.

---

## RB-04: LLM Budget Quota Exhaustion & Fallback Downgrade

**Trigger Alert:** `LLMBudgetExceeded` (Monthly expenditure > 90%)  
**Severity:** High  

### Immediate Actions:
1. **Verify Current Usage:**
   - Check Grafana dashboard `Nexus — LLM Cost, Tokens & Latency Monitoring`.
2. **Engage Model Routing Downgrade:**
   - Set environment variable `LLM_TIER_OVERRIDE="tier1_local"` in `.env`.
   - Non-critical workflows (e.g. initial answer sheet OCR summaries) switch to quantized local model.
3. **Request Quota Expansion or Credit Top-up:**
   - Contact model provider or platform administrator for enterprise budget increase.

---

## RB-05: External Connector Circuit Breaker Recovery

**Trigger Alert:** `ConnectorCircuitOpen` (Connector = `erp` / `lms` / `crm`)  
**Severity:** Warning / High  

### Immediate Actions:
1. **Check External Service Endpoint:**
   - Ping ERP/LMS health endpoint directly from the API container.
2. **Review Rate Limiting Headers:**
   - Check if external API returned `429 Too Many Requests`.
3. **Reset Circuit Breaker Manually:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/connectors/<CONNECTOR_NAME>/reset-circuit
   ```
4. **Drain Offline Queues:**
   - Any buffered sync actions stored in Redis will automatically retry with exponential backoff.

---

## RB-06: Database Failover, Restore & Disaster Recovery

**Trigger Event:** PostgreSQL node crash or disk corruption  
**Severity:** Disaster Recovery  

### Immediate Actions:
1. **Locate Latest Verified Automated Backup:**
   ```bash
   python backend/scripts/backup_restore.py --list
   ```
2. **Execute Full Restore & Verification:**
   ```bash
   python backend/scripts/backup_restore.py --restore --file <BACKUP_PATH>
   ```
3. **Verify Hash Chain Integrity Post-Restore:**
   ```bash
   python backend/scripts/backup_restore.py --verify-chain
   ```
4. **Bring API and Worker Online:**
   ```bash
   docker compose up -d api celery-worker
   ```

---

## RB-07: Brute Force & Credential Stuffing Emergency Lockout

**Trigger Alert:** `BruteForceSecurityAlert`  
**Severity:** Critical  

### Immediate Actions:
1. **Check Active Security Incidents:**
   - Open `/security` dashboard in Mission Control.
2. **Review Automated Containment Status:**
   - Verify that the offending IP address is present in `action_handler.list_active_blocks()`.
3. **Extend or Make IP Block Permanent:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/security/blocks -d '{"entity_type": "ip", "entity_value": "<IP>", "is_permanent": true}'
   ```
4. **Force Password Reset on Targeted Accounts:**
   - Invalidate active sessions via JTI blacklist and send security reset email.

---

## RB-08: Redis Connection Outage & Token Blacklist Fallback

**Trigger Event:** Redis container down or network partition  
**Severity:** High  

### Immediate Actions:
1. **Restart Redis Service:**
   ```bash
   docker restart nexus-redis
   ```
2. **Verify In-Memory Blacklist Fallback:**
   - Ensure `app/core/token_blacklist.py` is serving from local process memory cache.
3. **Test Session Token Revocation:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/logout
   ```

---

## RB-09: Production Secrets & Key Rotation

**Trigger Event:** Scheduled 90-day key rotation or credential exposure  
**Severity:** Standard Maintenance / P1  

### Immediate Actions:
1. **Generate New Secret Keys:**
   ```bash
   openssl rand -hex 32  # For JWT Secret
   openssl rand -hex 32  # For Webhook HMAC Secret
   ```
2. **Deploy Dual-Verification Config:**
   - Keep previous key in `JWT_PREVIOUS_SECRETS` for 1-hour grace period to avoid logging out active users.
3. **Update `.env` and Trigger Rolling Restart:**
   ```bash
   docker compose up -d --no-deps api
   ```

---

## RB-10: Celery Worker Deadlock & Queue Congestion Recovery

**Trigger Alert:** `QueueCongestionAlert` (Queue depth > 500 tasks)  
**Severity:** High  

### Immediate Actions:
1. **Inspect Celery Queue Depth:**
   ```bash
   docker exec -it nexus-redis redis-cli -n 1 llen celery
   ```
2. **Scale Worker Concurrency:**
   ```bash
   docker compose up -d --scale celery-worker=4
   ```
3. **Purge Corrupted Poison-Pill Tasks if Necessary:**
   ```bash
   docker exec -it nexus-celery-worker celery -A app.workers.celery_app purge -f
   ```
