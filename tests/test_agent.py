import pytest
from unittest.mock import MagicMock, patch
from app.agent.graph import build_graph, ReviewState, check_if_python, generate_report
from app.schemas import ReviewRequest
from pydantic import ValidationError


def make_state(code: str) -> ReviewState:
    return {
        "code": code,
        "is_python": False,
        "structure": "",
        "typing_issues": "",
        "quality_issues": "",
        "security_issues": "",
        "report": {},
    }


@patch("app.agent.graph.llm")
def test_check_if_python_yes(mock_llm):
    mock_llm.invoke.return_value = MagicMock(content="yes")
    result = check_if_python(make_state("def foo(): pass"))
    assert result["is_python"] is True


@patch("app.agent.graph.llm")
def test_check_if_python_no(mock_llm):
    mock_llm.invoke.return_value = MagicMock(content="no")
    result = check_if_python(make_state("console.log('hi')"))
    assert result["is_python"] is False


@patch("app.agent.graph.llm")
def test_generate_report_invalid_json(mock_llm):
    mock_llm.invoke.return_value = MagicMock(content="Invalid json{{")
    state = make_state("def foo(): pass")
    state["structure"] = "ok"
    result = generate_report(state)
    assert "error" in result["report"]


@patch("app.agent.graph.llm")
def test_full_graph_happy_path(mock_llm):
    mock_llm.invoke.side_effect = [
        MagicMock(content="yes"),
        MagicMock(content="structure ok"),
        MagicMock(content="no typing"),
        MagicMock(content="no quality"),
        MagicMock(content="no security"),
        MagicMock(
            content='{"score": 7, "issues": [], "suggestions": [], "summary": "ok"}'
        ),
    ]
    result = build_graph().invoke(make_state("def foo(): pass"))
    assert result["report"]["score"] == 7


def test_rejects_too_long_code():

    with pytest.raises(ValidationError):
        ReviewRequest(code="x" * 6000)


def test_empty_code():

    with pytest.raises(ValidationError):
        ReviewRequest(code="")
