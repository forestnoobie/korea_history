from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import quiz, images

app = FastAPI(title="Korea History Quiz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router)
app.include_router(images.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
