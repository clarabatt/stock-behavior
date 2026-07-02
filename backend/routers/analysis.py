from fastapi import APIRouter, Depends, HTTPException

from backend.database.models import User
from backend.schemas import AskQuestionRequest, AskQuestionResponse
from backend.services.ai_analysis import AiAnalysisError, ask_question
from backend.services.auth import get_current_user

router = APIRouter()


@router.post("/analysis/ask", response_model=AskQuestionResponse)
def ask(body: AskQuestionRequest, user: User = Depends(get_current_user)) -> AskQuestionResponse:
    try:
        result = ask_question(body.question)
    except AiAnalysisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return AskQuestionResponse(answer=result.answer, sql=result.sql, row_count=result.row_count)
