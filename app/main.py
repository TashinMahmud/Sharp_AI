
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from app.api.routes import (
    categories_router,
    topics_router,
    materials_router,
    training_router,
    users_router
)
from app.core.limiter import limiter

app = FastAPI(
    title="Sharp Ai",
    description="API for argumentation combat training and topic generation.",
    version="2.0.0",
    root_path="/ai",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(categories_router)
app.include_router(topics_router)
app.include_router(materials_router)
app.include_router(training_router)
app.include_router(users_router)


@app.get("/health")
@limiter.exempt
def health_check():
    return {"status": "ok"}
