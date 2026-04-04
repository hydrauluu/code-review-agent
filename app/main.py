from fastapi import FastAPI, UploadFile, File, HTTPException
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


@app.post("/review/file", response_model=ReviewResponse)
async def review_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are supported.")

    content = await file.read()

    try:
        code = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not read file.")

    result = graph.invoke(
        {
            "code": code,
            "is_python": False,
            "structure": "",
            "typing_issues": "",
            "quality_issues": "",
            "security_issues": "",
            "report": {},
        }
    )

    return ReviewResponse(**result["report"])
