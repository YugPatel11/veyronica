# Nexus API Reference (v1)

**Base URL:** `http://localhost:8000/api/v1`  
**Interactive Docs (Swagger UI):** `http://localhost:8000/docs`  
**Alternative Docs (ReDoc):** `http://localhost:8000/redoc`  
**OpenAPI Specification:** `http://localhost:8000/openapi.json`  

---

## 1. Authentication & Security Headers

All authenticated endpoints require an `Authorization` header containing a valid Bearer JWT:
```http
Authorization: Bearer <access_token>
X-Request-ID: <uuid>
Content-Type: application/json
```

For state-changing operations (`POST`, `PUT`, `DELETE`), include the CSRF token obtained via cookie:
```http
X-CSRF-Token: <csrf_token>
```

---

## 2. Core Endpoints

### 2.1 Authentication & Sessions

#### POST `/api/v1/auth/login`
Authenticates a user and issues an access JWT.
- **Request Body:**
  ```json
  {
    "email": "faculty@university.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_94a0f8",
      "email": "faculty@university.edu",
      "role": "faculty",
      "department": "Computer Science"
    }
  }
  ```

#### POST `/api/v1/auth/logout`
Revokes the current access token and blacklists the JTI in Redis.
- **Response (200 OK):** `{"message": "Logged out successfully"}`

---

### 2.2 WF1 — Exam Result Workflow

#### POST `/api/v1/exam-workflow/trigger`
Trigger end-to-end evaluation on an uploaded answer sheet.
- **Request Body:**
  ```json
  {
    "file_id": "file_exam_401.pdf",
    "subject": "CS301 Data Structures",
    "student_id": "std_1001",
    "rubric_id": "rub_ds_midterm"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "run_id": "run_98a72b",
    "status": "completed",
    "total_marks": 88.5,
    "max_marks": 100.0,
    "confidence": 0.94,
    "requires_review": false,
    "decision_hash": "a4f89b1c..."
  }
  ```

---

### 2.3 WF3 — Admin Copilot

#### POST `/api/v1/copilot/chat`
Ask natural language questions or request operations.
- **Request Body:**
  ```json
  {
    "query": "Show pass/fail distribution for CS301 section A",
    "user_role": "admin"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "format": "table",
    "content": "CS301 Section A pass rate is 92.4%",
    "data": [
      { "division": "A", "total_students": 60, "passed": 55, "failed": 5, "pass_rate": "91.7%" }
    ],
    "plan": null
  }
  ```

#### POST `/api/v1/copilot/confirm`
Execute a pending safe write operation using a confirmation token.
- **Request Body:**
  ```json
  {
    "confirmation_token": "cf_a89f30b912"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "executed",
    "action": "update_marks",
    "affected_records": 1,
    "timestamp": "2026-10-30T17:00:00Z"
  }
  ```

---

### 2.4 Cryptographic Decision Ledger

#### GET `/api/v1/audit`
Retrieve hash-chained audit ledger blocks.
- **Query Parameters:**
  - `limit` (default: 50)
  - `event_type` (`decision`, `action`, `security_incident`)
  - `run_id` (optional filter)
- **Response (200 OK):**
  ```json
  {
    "entries": [
      {
        "sequence_number": 42,
        "event_type": "decision",
        "action": "exam_evaluation",
        "previous_hash": "9f32e1...",
        "entry_hash": "c0182a...",
        "timestamp": "2026-10-30T16:55:00Z"
      }
    ],
    "chain_valid": true,
    "total_count": 42
  }
  ```

#### POST `/api/v1/audit/verify`
Recompute and verify SHA-256 hash chaining across all blocks.
- **Response (200 OK):**
  ```json
  {
    "is_valid": true,
    "last_verified_sequence": 42,
    "total_blocks": 42
  }
  ```

---

### 2.5 System Health & Telemetry

#### GET `/health`
Aggregated health status of API, database, Redis, and connectors.
- **Response (200 OK):**
  ```json
  {
    "status": "ok",
    "timestamp": "2026-10-30T17:00:00Z",
    "services": {
      "database": "connected",
      "redis": "connected",
      "storage": "connected"
    }
  }
  ```

#### GET `/metrics`
Prometheus metrics exposition format.
- **Response (200 OK, text/plain):**
  ```text
  # HELP nexus_http_requests_total Total HTTP requests handled
  # TYPE nexus_http_requests_total counter
  nexus_http_requests_total{method="GET",status="200"} 12480
  ```

---

## 3. Error Responses

Errors return a consistent JSON schema:
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please retry after 42 seconds.",
    "request_id": "7f8b90a1-9c88-410a-b51e-d456789abcde"
  }
}
```

Standard status codes:
- `400 Bad Request`: Input validation failed
- `401 Unauthorized`: Missing or expired JWT
- `403 Forbidden`: Insufficient role permissions
- `404 Not Found`: Resource does not exist
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server exception (masked)
