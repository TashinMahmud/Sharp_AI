
from app.api.routes.categories import router as categories_router
from app.api.routes.topics import router as topics_router
from app.api.routes.materials import router as materials_router
from app.api.routes.training import router as training_router

__all__ = [
    "categories_router",
    "topics_router",
    "materials_router",
    "training_router"
]
