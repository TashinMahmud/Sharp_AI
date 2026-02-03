"""FastAPI application entry point."""

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import debate_router
from app.core.limiter import limiter

app = FastAPI(
    title="Debate Quiz API",
    description="API for generating debate arguments, quiz questions, hints, and evaluations",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(debate_router)


@app.get("/health")
@limiter.exempt
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}
