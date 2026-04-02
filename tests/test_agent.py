import pytest
from unittest.mock import MagicMock, patch
from app.agent.graph import build_graph, ReviewState


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
def test_rejects_non_python(mock_llm):
    mock_llm.invoke.return_value = MagicMock(content="no")
    graph = build_graph()
    result = graph.invoke(make_state("console.log('hello')"))
    assert result["report"]["error"] == "Only Python code is supported."


@patch("app.agent.graph.llm")
def test_accepts_python(mock_llm):
    mock_llm.invoke.return_value = MagicMock(
        content='{"score": 7, "issues": [], "suggestions": [], "summary": "ok"}'
    )
    mock_llm.invoke.side_effect = [
        MagicMock(content="yes"),  # check_if_python
        MagicMock(content="structure ok"),  # analyze_structure
        MagicMock(content="no typing"),  # check_typing
        MagicMock(content="no quality"),  # check_quality
        MagicMock(content="no security"),  # check_security
        MagicMock(
            content='{"score": 7, "issues": [], "suggestions": [], "summary": "ok"}'
        ),  # generate_report
    ]
    graph = build_graph()
    result = graph.invoke(make_state("def foo(): pass"))
    assert "error" not in result["report"]


def test_rejects_too_long_code():
    from app.schemas import ReviewRequest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ReviewRequest(code="x" * 6000)


def test_empty_code():
    from app.schemas import ReviewRequest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ReviewRequest(code="")
