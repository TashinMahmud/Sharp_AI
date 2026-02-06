
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from app.api.routes import (
    categories_router,
    topics_router,
    materials_router,
    training_router
)
from app.core.limiter import limiter

app = FastAPI(
    title="FastAPI Quiz API",
    description="API for argumentation training: generate arguments, quizzes, hints, and evaluations",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(categories_router)
app.include_router(topics_router)
app.include_router(materials_router)
app.include_router(training_router)


@app.get("/health")
@limiter.exempt
def health_check():
    return {"status": "ok"}
