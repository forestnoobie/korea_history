"""In-memory session store for quiz sessions."""
from typing import Dict, Optional
from ..models.quiz import QuizState, QuizQuestionInternal

# Maps session_id → QuizState
_sessions: Dict[str, QuizState] = {}

# Maps session_id → list of internal questions (with answers, server-side only)
_internal_questions: Dict[str, Dict[str, QuizQuestionInternal]] = {}


def save_session(state: QuizState, internal_qs: Dict[str, QuizQuestionInternal]) -> None:
    _sessions[state.session_id] = state
    _internal_questions[state.session_id] = internal_qs


def get_session(session_id: str) -> Optional[QuizState]:
    return _sessions.get(session_id)


def get_internal_questions(session_id: str) -> Optional[Dict[str, QuizQuestionInternal]]:
    return _internal_questions.get(session_id)


def update_session(state: QuizState) -> None:
    _sessions[state.session_id] = state
