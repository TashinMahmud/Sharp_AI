"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes import debate_router

app = FastAPI(
    title="Debate Quiz API",
    description="API for generating debate arguments, quiz questions, hints, and evaluations",
    version="1.0.0",
)

app.include_router(debate_router)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}
