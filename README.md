# ZeloraTech HR Automation Engine

Multi-agent task routing and memory engine for HR automation — ZeloraTech Technical Assessment.

---

## Architecture

```
POST /api/v1/request
        │
        ▼
  Orchestrator Agent
  ┌─────────────────────────────────────────┐
  │  1. Retrieve memory context (STM + LTM) │
  │  2. Classify intent + confidence score  │
  │  3. Route to sub-agent                  │
  │  4. Inject memory into sub-agent prompt │
  │  5. Store turn in STM                   │
  └─────────────────────────────────────────┘
        │
   ┌────┴────────────────────────────┐
   ▼         ▼           ▼           ▼
Scheduling  Leave   Compliance  Clarification
  Agent     Agent     Agent       Agent
        │
        ▼
   Audit Log (append-only SQLite)
```

### Sub-Agents

| Agent | Handles |
|---|---|
| `scheduling_agent` | meetings, interviews, shifts |
| `leave_agent` | vacation, sick leave, PTO |
| `compliance_agent` | policies, regulations, code of conduct |
| `clarification_agent` | ambiguous or unclear requests |

### Two-Tier Memory System

- **STM** (Short-Term Memory) — conversational history for context
- **LTM** (Long-Term Memory) — persistent key-value facts per user (department, role, etc.)

---

## Setup & Installation

### 1. Unzip the project (or clone the repository)

Extract the contents into your desired directory and navigate into the project folder.

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a new file named `.env` in the root directory and add your API key:

```env
GEMINI_API_KEY="your_api_key_here"
```

> **Note:** The original starter architecture utilized Anthropic, but this implementation was optimized to use Google Gemini for cost-efficiency, reliable JSON formatting, and high performance during local development.

### 5. Run the server

```bash
python run.py
```

- Server starts at: `http://localhost:8000`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

---

## API Endpoints

### 1. Health Check

```
GET /api/v1/health
```

### 2. Add Long-Term Memory

```
POST /api/v1/memory/emp_12345/ltm
```

```json
{
  "key": "department",
  "value": "Computer Science"
}
```

### 3. Submit a Request (Orchestrator)

```
POST /api/v1/request
```

```json
{
  "user_id": "emp_12345",
  "message": "I need to take next Friday off for a doctor's appointment."
}
```

### 4. Check Current Memory

```
GET /api/v1/memory/emp_12345
```

### 5. Retrieve Audit Logs

```
GET /api/v1/audit?user_id=emp_12345
```

### 6. Delete a Long-Term Memory Fact

```
DELETE /api/v1/memory/emp_12345/ltm/department
```

### 7. Clear Short-Term Memory

```
DELETE /api/v1/memory/emp_12345/stm
```

---

## Testing with Postman

All 7 endpoints were tested using Postman. You can copy and paste each URL directly into Postman to verify the system end-to-end.

> Make sure the server is running (`python run.py`) before sending requests.

| # | Method | URL |
|---|--------|-----|
| 1 | `GET` | `http://localhost:8000/api/v1/health` |
| 2 | `POST` | `http://localhost:8000/api/v1/memory/emp_12345/ltm` |
| 3 | `POST` | `http://localhost:8000/api/v1/request` |
| 4 | `GET` | `http://localhost:8000/api/v1/memory/emp_12345` |
| 5 | `GET` | `http://localhost:8000/api/v1/audit?user_id=emp_12345` |
| 6 | `DELETE` | `http://localhost:8000/api/v1/memory/emp_12345/ltm/department` |
| 7 | `DELETE` | `http://localhost:8000/api/v1/memory/emp_12345/stm` |

**Request bodies for POST endpoints:**

POST `http://localhost:8000/api/v1/memory/emp_12345/ltm`
```json
{
  "key": "department",
  "value": "Computer Science"
}
```

POST `http://localhost:8000/api/v1/request`
```json
{
  "user_id": "emp_12345",
  "message": "I need to take next Friday off for a doctor's appointment."
}
```

You can also use the interactive Swagger UI at `http://localhost:8000/docs` to test all endpoints directly in your browser.

---

## Project Structure

```
zelora_hr_agent/
├── app/
│   ├── main.py               # FastAPI app + lifespan
│   ├── database.py           # SQLite init + connection
│   ├── agents/
│   │   ├── __init__.py
│   │   └── orchestrator.py   # Intent classification + routing
│   ├── memory/
│   │   └── memory_store.py   # STM + LTM operations
│   ├── audit/
│   │   └── audit_log.py      # Append-only audit log
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   └── routers/
│       ├── requests.py       # POST /request
│       ├── audit.py          # GET /audit
│       ├── memory.py         # Memory CRUD
│       └── health.py         # GET /health
├── tests/
├── .env
├── requirements.txt
└── run.py
```
