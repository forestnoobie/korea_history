from fastapi import APIRouter, Depends, Query

from ..dependencies import get_opensearch_service
from ..models.quiz import AnswerSubmission, QuizResult, QuizState
from ..services import quiz_service
from ..services.opensearch_service import OpenSearchService

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/start", response_model=QuizState)
def start_quiz(
    count: int = Query(default=5, ge=1, le=50),
    exam_id: str = Query(default="74"),
    service: OpenSearchService = Depends(get_opensearch_service),
):
    """Create a new quiz session with `count` random questions."""
    return quiz_service.create_session(exam_id=exam_id, count=count, service=service)


@router.get("/{session_id}", response_model=QuizState)
def get_session(session_id: str):
    """Return the current session state (answers visible, correct answers hidden)."""
    return quiz_service._get_or_404(session_id)


@router.post("/{session_id}/answer", response_model=QuizState)
def submit_answer(session_id: str, body: AnswerSubmission):
    """Record one answer for the session."""
    return quiz_service.record_answer(session_id, body)


@router.post("/{session_id}/submit", response_model=QuizResult)
def submit_quiz(session_id: str):
    """Finalize the quiz and return the scored result."""
    return quiz_service.submit_quiz(session_id)


@router.get("/{session_id}/review", response_model=QuizResult)
def review(session_id: str):
    """Return the scored result including correct answers for wrong questions."""
    return quiz_service.get_review(session_id)
