#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# ---------------------------------------------------------------------------
# 1. OpenSearch
# ---------------------------------------------------------------------------
echo "[1/4] Starting OpenSearch..."
if docker ps --format "{{.Names}}" | grep -q "^es01$"; then
    echo "      OpenSearch already running — skipping."
else
    bash "$SCRIPT_DIR/opensearch.sh"
    echo "      Waiting for OpenSearch to be ready..."
    for i in $(seq 1 30); do
        STATUS=$(curl -sf http://localhost:9200/_cluster/health 2>/dev/null \
                 | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "")
        [ "$STATUS" = "green" ] || [ "$STATUS" = "yellow" ] && break
        sleep 3
    done
    echo "      OpenSearch ready."
fi

# ---------------------------------------------------------------------------
# 2. Seed data (only if index is empty)
# ---------------------------------------------------------------------------
echo "[2/4] Checking index data..."
cd "$PROJECT_ROOT"
DOC_COUNT=$(curl -sf http://localhost:9200/history_exam_bbox/_count 2>/dev/null \
            | python3 -c "import sys,json; print(json.load(sys.stdin).get('count',0))" 2>/dev/null || echo "0")

if [ "$DOC_COUNT" -eq 0 ] 2>/dev/null; then
    echo "      Index empty — inserting bbox data and migrating answers..."
    python insert_to_opensearch.py
    python scripts/migrate_answers.py --exam-no 74 --answer-csv "data/74회 심화 정답표.csv"
else
    echo "      Index has $DOC_COUNT docs — skipping seed."
fi

# ---------------------------------------------------------------------------
# 3. Backend (FastAPI on :8000)
# ---------------------------------------------------------------------------
echo "[3/4] Starting backend on :8000..."
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "      Port 8000 already in use — skipping."
else
    nohup python -m uvicorn app.main:app --reload --port 8000 \
        > /tmp/korea-backend.log 2>&1 &
    echo "      Backend PID: $! — logs: /tmp/korea-backend.log"
fi

# ---------------------------------------------------------------------------
# 4. Frontend (Next.js on :8003)
# ---------------------------------------------------------------------------
echo "[4/4] Starting frontend on :8003..."
if lsof -ti:8003 >/dev/null 2>&1; then
    echo "      Port 8003 already in use — skipping."
else
    nohup bash -c '. "$HOME/.nvm/nvm.sh" && cd '"$PROJECT_ROOT/frontend"' && npm run dev -- -p 8003' \
        > /tmp/korea-frontend.log 2>&1 &
    echo "      Frontend PID: $! — logs: /tmp/korea-frontend.log"
fi

# ---------------------------------------------------------------------------
echo ""
echo "All services started:"
echo "  Frontend  → http://localhost:8003"
echo "  Backend   → http://localhost:8000"
echo "  OpenSearch→ http://localhost:9200"
echo ""
echo "To stop everything:"
echo "  bash scripts/stop.sh"
