# Code Review Agent

AI-powered Python code review agent built with LangGraph and FastAPI.
Analyzes Python code for typing issues, code quality, and security vulnerabilities.

## What it does

Accepts Python code via REST API and returns a structured review report with:
- **Score** (0–10)
- **Issues** — typing, quality, security, structure with severity levels
- **Suggestions** — concrete improvements
- **Summary** — overall assessment

Non-Python code is rejected automatically.

## Agent flow
```
check_if_python → analyze_structure → check_typing → check_quality → check_security → generate_report
```

## Project structure
```
├── app/
│   ├── agent/
│   │   ├── graph.py      # LangGraph agent definition
│   │   └── tools.py
│   ├── main.py           # FastAPI endpoints
│   └── schemas.py        # Pydantic models
├── requirements.txt
└── README.md
```

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` file in project root:
```
GOOGLE_API_KEY=your_key_here
```

## Run
```bash
uvicorn app.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`

## Usage
```bash
curl -X POST http://127.0.0.1:8000/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b):\n    return a + b"}'
```

## Limitations

- Python only, max 5000 characters
- 5 sequential LLM calls per request — slow on large inputs
- Depends on Gemini API quota
- LLM may hallucinate issues
