"""Pytest fixtures shared across test modules."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.dependencies import get_opensearch_service
from app.services.opensearch_service import OpenSearchService
from app.models.quiz import QuizQuestionInternal

FIXTURE_QUESTIONS = [
    QuizQuestionInternal(
        question_no=i,
        exam_id="74",
        image_path=f"data/processed/history_exam/74/problem_image/74_workbook_page_1_q{i}.png",
        points=2,
        answer=i % 5 + 1,
    )
    for i in range(1, 6)
]


def mock_opensearch_service() -> OpenSearchService:
    svc = MagicMock(spec=OpenSearchService)
    svc.get_random_questions.return_value = FIXTURE_QUESTIONS
    return svc


@pytest.fixture()
def client():
    app.dependency_overrides[get_opensearch_service] = mock_opensearch_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
