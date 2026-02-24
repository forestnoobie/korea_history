from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class QuizQuestion(BaseModel):
    """Question data sent to the client — no answer field."""
    question_no: int
    exam_id: str
    image_path: str
    points: int


class QuizQuestionInternal(QuizQuestion):
    """Extended model used only server-side; includes the correct answer."""
    answer: int


class AnswerSubmission(BaseModel):
    question_no: int
    exam_id: str
    selected_answer: int  # 1-5


class QuizState(BaseModel):
    session_id: str
    exam_id: str
    questions: List[QuizQuestion]
    answers: Dict[str, int] = {}   # key: "{exam_id}_{question_no}"
    submitted: bool = False
    total_questions: int = 0

    @property
    def answer_key(self) -> str:
        # not used as a pydantic field — just a helper
        return ""


class QuestionResult(BaseModel):
    question_no: int
    exam_id: str
    image_path: str
    selected_answer: Optional[int]
    correct_answer: int
    is_correct: bool
    points: int
    points_earned: int


class QuizResult(BaseModel):
    session_id: str
    score: int          # number of correct answers
    total: int
    points_earned: int
    total_points: int
    results: List[QuestionResult]
