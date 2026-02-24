"""OpenSearch queries for the quiz application."""
import logging
from typing import List, Optional

from opensearchpy import OpenSearch

from ..config import settings
from ..models.quiz import QuizQuestionInternal

logger = logging.getLogger(__name__)


def _build_client() -> OpenSearch:
    auth = (
        (settings.opensearch_username, settings.opensearch_password)
        if settings.opensearch_username
        else None
    )
    return OpenSearch(
        hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
        http_auth=auth,
        use_ssl=settings.opensearch_use_ssl,
        verify_certs=False,
        ssl_show_warn=False,
    )


class OpenSearchService:
    def __init__(self, client: Optional[OpenSearch] = None):
        self._client = client or _build_client()

    def get_random_questions(
        self, exam_id: str, count: int = 5
    ) -> List[QuizQuestionInternal]:
        """
        Return `count` random questions for the given exam that have an answer.
        Uses function_score with random_score to avoid a full scan.
        """
        query = {
            "size": count,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"exam_id": exam_id}},
                                {"term": {"artifact_type": "question"}},
                                {"exists": {"field": "answer"}},
                            ]
                        }
                    },
                    "functions": [{"random_score": {}}],
                    "score_mode": "sum",
                }
            },
        }

        try:
            resp = self._client.search(index=settings.opensearch_index, body=query)
        except Exception as exc:
            logger.error("OpenSearch query failed: %s", exc)
            raise

        questions: List[QuizQuestionInternal] = []
        for hit in resp["hits"]["hits"]:
            src = hit["_source"]
            try:
                q = QuizQuestionInternal(
                    question_no=int(src["question_no"]),
                    exam_id=src["exam_id"],
                    image_path=src["image_path"],
                    points=int(src.get("points", 2)),
                    answer=int(src["answer"]),
                )
                questions.append(q)
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping malformed hit %s: %s", hit["_id"], exc)

        return questions
