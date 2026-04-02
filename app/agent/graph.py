from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json
import re

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


class ReviewState(TypedDict):
    code: str
    is_python: bool
    structure: str
    typing_issues: str
    quality_issues: str
    security_issues: str
    report: dict


def check_if_python(state: ReviewState) -> ReviewState:
    prompt = """Is the following code written in Python? Reply with only "yes" or "no".
    
Code:
{code}""".format(code=state["code"])
    response = llm.invoke(prompt)
    is_python = response.content.strip().lower().startswith("yes")
    return {**state, "is_python": is_python}


def reject(state: ReviewState) -> ReviewState:
    return {
        **state,
        "report": {
            "error": "Only Python code is supported.",
            "issues": [],
            "suggestions": [],
            "score": None,
        },
    }


def analyze_structure(state: ReviewState) -> ReviewState:
    prompt = """Analyze the structure of this Python code.
List: functions, classes, imports, and overall organization.
Be concise.

Code:
{code}""".format(code=state["code"])
    response = llm.invoke(prompt)
    return {**state, "structure": response.content}


def check_typing(state: ReviewState) -> ReviewState:
    prompt = """Review the type annotations in this Python code.
Check for:
- Missing type hints on function arguments and return types
- Incorrect use of Optional, Union, List, Dict etc.
- Missing Pydantic model validation if applicable
- Any type-unsafe patterns

Code:
{code}""".format(code=state["code"])
    response = llm.invoke(prompt)
    return {**state, "typing_issues": response.content}


def check_quality(state: ReviewState) -> ReviewState:
    prompt = """Review the code quality of this Python code.
Check for:
- Poor naming conventions
- Missing or incomplete docstrings
- Functions that are too complex or too long
- Code duplication
- Violations of PEP8

Code:
{code}""".format(code=state["code"])
    response = llm.invoke(prompt)
    return {**state, "quality_issues": response.content}


def check_security(state: ReviewState) -> ReviewState:
    prompt = """Review this Python code for security issues.
Check for:
- Use of eval() or exec()
- SQL injection vulnerabilities
- Files opened without context manager
- Hardcoded secrets or passwords
- Unsafe deserialization

Code:
{code}""".format(code=state["code"])
    response = llm.invoke(prompt)
    return {**state, "security_issues": response.content}


def generate_report(state: ReviewState) -> ReviewState:
    prompt = """You are a senior Python code reviewer.
Based on the analysis below, generate a structured code review report.

Structure analysis:
{structure}

Typing issues:
{typing_issues}

Code quality issues:
{quality_issues}

Security issues:
{security_issues}

Respond ONLY with a valid JSON object in this exact format, no markdown, no extra text:
{{
  "score": <integer from 0 to 10>,
  "issues": [
    {{"type": "typing|quality|security|structure", "severity": "low|medium|high", "description": "..."}}
  ],
  "suggestions": [
    "suggestion 1",
    "suggestion 2"
  ],
  "summary": "overall summary in 2-3 sentences"
}}""".format(
        structure=state["structure"],
        typing_issues=state["typing_issues"],
        quality_issues=state["quality_issues"],
        security_issues=state["security_issues"],
    )

    response = llm.invoke(prompt)

    raw = response.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"```$", "", raw).strip()

    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        report = {"error": "Failed to parse report", "raw": raw}

    return {**state, "report": report}


def route_after_check(state: ReviewState) -> str:
    if state["is_python"]:
        return "analyze_structure"
    return "reject"


def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("check_if_python", check_if_python)
    graph.add_node("reject", reject)
    graph.add_node("analyze_structure", analyze_structure)
    graph.add_node("check_typing", check_typing)
    graph.add_node("check_quality", check_quality)
    graph.add_node("check_security", check_security)
    graph.add_node("generate_report", generate_report)

    graph.set_entry_point("check_if_python")

    graph.add_conditional_edges(
        "check_if_python",
        route_after_check,
        {"analyze_structure": "analyze_structure", "reject": "reject"},
    )

    graph.add_edge("reject", END)
    graph.add_edge("analyze_structure", "check_typing")
    graph.add_edge("check_typing", "check_quality")
    graph.add_edge("check_quality", "check_security")
    graph.add_edge("check_security", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()


if __name__ == "__main__":
    agent = build_graph()
    test_code = """
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
    result = agent.invoke(
        {
            "code": test_code,
            "is_python": False,
            "structure": "",
            "typing_issues": "",
            "quality_issues": "",
            "security_issues": "",
            "report": {},
        }
    )
    print(json.dumps(result["report"], indent=2))
