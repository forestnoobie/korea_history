#!/usr/bin/env python3
"""
Migrate answer and points data into OpenSearch documents.

Reads an answer CSV (문항번호, 정답, 배점) and updates each matching
document in the history_exam_bbox index with `answer` and `points` fields.

Usage:
    python scripts/migrate_answers.py \
        --exam-no 74 \
        --answer-csv "data/74회 심화 정답표.csv"
"""

import argparse
import logging
import os
import sys

import pandas as pd
from opensearchpy import OpenSearch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INDEX_NAME = "history_exam_bbox"


def build_client() -> OpenSearch:
    return OpenSearch(
        hosts=[{
            "host": os.environ.get("OPENSEARCH_HOST", "localhost"),
            "port": int(os.environ.get("OPENSEARCH_PORT", 9200)),
        }],
        http_auth=(
            os.environ.get("OPENSEARCH_USERNAME"),
            os.environ.get("OPENSEARCH_PASSWORD"),
        ) if os.environ.get("OPENSEARCH_USERNAME") else None,
        use_ssl=os.environ.get("OPENSEARCH_USE_SSL", "false").lower() == "true",
        verify_certs=False,
        ssl_show_warn=False,
    )


def put_mapping(client: OpenSearch) -> None:
    """Add answer and points fields to the existing index mapping."""
    body = {
        "properties": {
            "answer": {"type": "integer"},
            "points": {"type": "integer"},
        }
    }
    client.indices.put_mapping(index=INDEX_NAME, body=body)
    logger.info("Mapping updated with 'answer' and 'points' fields.")


def migrate(client: OpenSearch, exam_id: str, df: pd.DataFrame) -> None:
    """Update each question document with its answer and points."""
    ok = 0
    failed = 0

    for _, row in df.iterrows():
        question_no = int(row["문항번호"])
        answer = int(row["정답"])
        points = int(row["배점"])

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"exam_id": exam_id}},
                        {"term": {"question_no": float(question_no)}},
                        {"term": {"artifact_type": "question"}},
                    ]
                }
            },
            "script": {
                "source": "ctx._source.answer = params.answer; ctx._source.points = params.points;",
                "lang": "painless",
                "params": {"answer": answer, "points": points},
            },
        }

        try:
            resp = client.update_by_query(index=INDEX_NAME, body=query, refresh=True)
            updated = resp.get("updated", 0)
            if updated == 0:
                logger.warning(
                    f"No document found for exam_id={exam_id}, question_no={question_no}"
                )
                failed += 1
            else:
                logger.debug(f"Updated question {question_no}: answer={answer}, points={points}")
                ok += 1
        except Exception as exc:
            logger.error(f"Error updating question {question_no}: {exc}")
            failed += 1

    logger.info(f"Migration complete — updated: {ok}, failed: {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate answers into OpenSearch")
    parser.add_argument("--exam-no", type=int, default=74, help="Exam number (default: 74)")
    parser.add_argument(
        "--answer-csv",
        default="data/74회 심화 정답표.csv",
        help="Path to answer CSV (columns: 문항번호, 정답, 배점)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.answer_csv):
        logger.error(f"Answer CSV not found: {args.answer_csv}")
        sys.exit(1)

    df = pd.read_csv(args.answer_csv)
    required = {"문항번호", "정답", "배점"}
    if not required.issubset(df.columns):
        logger.error(f"CSV must have columns {required}; got {set(df.columns)}")
        sys.exit(1)

    logger.info(f"Loaded {len(df)} answers from {args.answer_csv}")

    client = build_client()
    health = client.cluster.health()
    logger.info(f"OpenSearch cluster health: {health['status']}")

    if not client.indices.exists(index=INDEX_NAME):
        logger.error(f"Index '{INDEX_NAME}' does not exist. Run insert_to_opensearch.py first.")
        sys.exit(1)

    put_mapping(client)
    migrate(client, str(args.exam_no), df)


if __name__ == "__main__":
    main()
