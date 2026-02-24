"""Quiz session logic: creation, answer submission, scoring."""
import uuid
from typing import List, Optional

from fastapi import HTTPException

from ..models.quiz import (
    AnswerSubmission,
    QuestionResult,
    QuizQuestion,
    QuizQuestionInternal,
    QuizResult,
    QuizState,
)
from ..store import session_store
from .opensearch_service import OpenSearchService


def _answer_key(exam_id: str, question_no: int) -> str:
    return f"{exam_id}_{question_no}"


def create_session(exam_id: str, count: int, service: OpenSearchService) -> QuizState:
    internal_qs = service.get_random_questions(exam_id=exam_id, count=count)
    if not internal_qs:
        raise HTTPException(status_code=404, detail="No questions found for this exam.")

    session_id = str(uuid.uuid4())

    public_qs: List[QuizQuestion] = [
        QuizQuestion(
            question_no=q.question_no,
            exam_id=q.exam_id,
            image_path=q.image_path,
            points=q.points,
        )
        for q in internal_qs
    ]

    state = QuizState(
        session_id=session_id,
        exam_id=exam_id,
        questions=public_qs,
        total_questions=len(public_qs),
    )

    internal_map = {
        _answer_key(q.exam_id, q.question_no): q for q in internal_qs
    }
    session_store.save_session(state, internal_map)
    return state


def record_answer(session_id: str, submission: AnswerSubmission) -> QuizState:
    state = _get_or_404(session_id)
    if state.submitted:
        raise HTTPException(status_code=409, detail="Quiz already submitted.")

    key = _answer_key(submission.exam_id, submission.question_no)
    state.answers[key] = submission.selected_answer
    session_store.update_session(state)
    return state


def submit_quiz(session_id: str) -> QuizResult:
    state = _get_or_404(session_id)
    if state.submitted:
        raise HTTPException(status_code=409, detail="Quiz already submitted.")

    internal_map = session_store.get_internal_questions(session_id)
    if not internal_map:
        raise HTTPException(status_code=500, detail="Session data corrupted.")

    results = _score(state, internal_map)
    state.submitted = True
    session_store.update_session(state)

    correct = sum(1 for r in results if r.is_correct)
    points_earned = sum(r.points_earned for r in results)
    total_points = sum(r.points for r in results)

    return QuizResult(
        session_id=session_id,
        score=correct,
        total=len(results),
        points_earned=points_earned,
        total_points=total_points,
        results=results,
    )


def get_review(session_id: str) -> QuizResult:
    """Return the scored result; exposes correct answers for wrong questions."""
    state = _get_or_404(session_id)
    if not state.submitted:
        raise HTTPException(status_code=400, detail="Quiz not yet submitted.")

    internal_map = session_store.get_internal_questions(session_id)
    if not internal_map:
        raise HTTPException(status_code=500, detail="Session data corrupted.")

    results = _score(state, internal_map)
    correct = sum(1 for r in results if r.is_correct)
    points_earned = sum(r.points_earned for r in results)
    total_points = sum(r.points for r in results)

    return QuizResult(
        session_id=session_id,
        score=correct,
        total=len(results),
        points_earned=points_earned,
        total_points=total_points,
        results=results,
    )


def _score(
    state: QuizState,
    internal_map: dict,
) -> List[QuestionResult]:
    results = []
    for q in state.questions:
        key = _answer_key(q.exam_id, q.question_no)
        internal: Optional[QuizQuestionInternal] = internal_map.get(key)
        if not internal:
            continue
        selected = state.answers.get(key)
        is_correct = selected == internal.answer
        results.append(
            QuestionResult(
                question_no=q.question_no,
                exam_id=q.exam_id,
                image_path=q.image_path,
                selected_answer=selected,
                correct_answer=internal.answer,
                is_correct=is_correct,
                points=internal.points,
                points_earned=internal.points if is_correct else 0,
            )
        )
    return results


def _get_or_404(session_id: str) -> QuizState:
    state = session_store.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found.")
    return state
