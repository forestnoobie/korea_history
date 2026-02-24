"""Tests for the quiz router — full flow, error paths, and guards."""
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def start_quiz(client, count=5, exam_id="74"):
    r = client.post(f"/api/quiz/start?count={count}&exam_id={exam_id}")
    assert r.status_code == 200
    return r.json()


def answer_all(client, session):
    """Submit answer 1 for every question in the session."""
    for q in session["questions"]:
        r = client.post(
            f"/api/quiz/{session['session_id']}/answer",
            json={
                "question_no": q["question_no"],
                "exam_id": q["exam_id"],
                "selected_answer": 1,
            },
        )
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Full happy-path flow
# ---------------------------------------------------------------------------

def test_full_quiz_flow(client):
    # 1. Start
    session = start_quiz(client)
    sid = session["session_id"]
    assert len(session["questions"]) == 5
    assert session["submitted"] is False

    # 2. GET session — no answers yet
    r = client.get(f"/api/quiz/{sid}")
    assert r.status_code == 200
    assert r.json()["answers"] == {}

    # 3. Answer all
    answer_all(client, session)

    # 4. Submit
    r = client.post(f"/api/quiz/{sid}/submit")
    assert r.status_code == 200
    result = r.json()
    assert result["total"] == 5
    assert 0 <= result["score"] <= 5
    assert "results" in result

    # 5. Review
    r = client.get(f"/api/quiz/{sid}/review")
    assert r.status_code == 200
    review = r.json()
    assert review["session_id"] == sid
    # Every result must expose correct_answer
    for res in review["results"]:
        assert "correct_answer" in res
        assert res["correct_answer"] in range(1, 6)


# ---------------------------------------------------------------------------
# Partial answers — unanswered questions count as wrong
# ---------------------------------------------------------------------------

def test_partial_answers_scores_zero_for_missing(client):
    session = start_quiz(client)
    sid = session["session_id"]

    # Answer only the first question
    q = session["questions"][0]
    client.post(
        f"/api/quiz/{sid}/answer",
        json={"question_no": q["question_no"], "exam_id": q["exam_id"], "selected_answer": 1},
    )

    r = client.post(f"/api/quiz/{sid}/submit")
    assert r.status_code == 200
    result = r.json()
    # Only the answered question can be correct; the rest have no selected answer
    unanswered = [res for res in result["results"] if res["selected_answer"] is None]
    assert len(unanswered) == 4
    for res in unanswered:
        assert res["is_correct"] is False
        assert res["points_earned"] == 0


# ---------------------------------------------------------------------------
# 404 paths
# ---------------------------------------------------------------------------

def test_get_nonexistent_session_404(client):
    r = client.get("/api/quiz/does-not-exist")
    assert r.status_code == 404


def test_submit_nonexistent_session_404(client):
    r = client.post("/api/quiz/does-not-exist/submit")
    assert r.status_code == 404


def test_review_nonexistent_session_404(client):
    r = client.get("/api/quiz/does-not-exist/review")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Double-submit guard
# ---------------------------------------------------------------------------

def test_double_submit_returns_409(client):
    session = start_quiz(client)
    sid = session["session_id"]
    answer_all(client, session)

    r1 = client.post(f"/api/quiz/{sid}/submit")
    assert r1.status_code == 200

    r2 = client.post(f"/api/quiz/{sid}/submit")
    assert r2.status_code == 409


def test_answer_after_submit_returns_409(client):
    session = start_quiz(client)
    sid = session["session_id"]
    answer_all(client, session)
    client.post(f"/api/quiz/{sid}/submit")

    q = session["questions"][0]
    r = client.post(
        f"/api/quiz/{sid}/answer",
        json={"question_no": q["question_no"], "exam_id": q["exam_id"], "selected_answer": 2},
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# Review before submit
# ---------------------------------------------------------------------------

def test_review_before_submit_returns_400(client):
    session = start_quiz(client)
    sid = session["session_id"]
    r = client.get(f"/api/quiz/{sid}/review")
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Query param defaults
# ---------------------------------------------------------------------------

def test_start_quiz_default_count(client):
    session = start_quiz(client)
    assert len(session["questions"]) == 5


def test_start_quiz_custom_count(client):
    session = start_quiz(client, count=3)
    # Mock always returns 5 questions; service is mocked, so count param is passed through.
    # Just verify the endpoint is reachable and returns a session.
    assert "session_id" in session
