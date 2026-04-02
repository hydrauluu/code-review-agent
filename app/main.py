from fastapi import FastAPI
from app.schemas import ReviewRequest, ReviewResponse
from app.agent.graph import build_graph

app = FastAPI(title="Python Code Review Agent")
graph = build_graph()


@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest):
    result = graph.invoke(
        {
            "code": request.code,
            "is_python": False,
            "structure": "",
            "typing_issues": "",
            "quality_issues": "",
            "security_issues": "",
            "report": {},
        }
    )
    return ReviewResponse(**result["report"])
