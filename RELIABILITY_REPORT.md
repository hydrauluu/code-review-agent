# Agent Reliability Report

## Overview
Python Code Review Agent based on LangGraph + Gemini 2.5 Flash.
Tested with pytest + mocks, no real LLM calls during tests.

## Test Results
| Test | Status |
|------|--------|
| Rejects non-Python code | ✅ PASSED |
| Accepts valid Python code | ✅ PASSED |
| Rejects code > 5000 chars | ✅ PASSED |
| Rejects empty code | ✅ PASSED |

## Edge Cases

| Input | Expected | Result |
|-------|----------|--------|
| JavaScript code | Rejected at check_if_python | ✅ |
| Empty string | ValidationError | ✅ |
| Code > 5000 chars | ValidationError | ✅ |
| Valid Python, no type hints | Review with issues | ✅ |

## Known Risks

| Risk | Severity | Notes |
|------|----------|-------|
| LLM hallucinations | Medium | Agent may report false issues |
| Gemini API quota exhaustion | High | Free tier has strict limits |
| Slow response (~10-15s) | Medium | 5 sequential LLM calls |
| Large codebase | High | Max 5000 chars, no chunking |
| JSON parse failure | Low | Handled with fallback error |

## Conclusion
Agent handles basic validation reliably via Pydantic.
Core risk is LLM non-determinism — same code may get different scores on repeated runs.
Not recommended for production without rate limiting and response caching.
