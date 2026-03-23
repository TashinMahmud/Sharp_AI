from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import List
import logging

from openai import APIError, APIConnectionError, AuthenticationError, RateLimitError

from app.core.limiter import limiter
from app.models.topic import TopicCreate, TopicResponse
from app.models.material import MaterialGenerate, MaterialResponse
from app.services.topic_service import get_topic_service
from app.services.material_service import get_material_service
from app.services.ai_service import get_ai_service
from app.schemas import TopicGenerateRequest, TopicGenerateResponse

router = APIRouter(prefix="/topics", tags=["topics"])
logger = logging.getLogger(__name__)


def _handle_ai_errors(e: Exception) -> HTTPException:
    if isinstance(e, RateLimitError):
        return HTTPException(status_code=429, detail="AI rate limit exceeded. Try again shortly.")
    if isinstance(e, AuthenticationError):
        return HTTPException(status_code=401, detail="Invalid AI API key.")
    if isinstance(e, (APIError, APIConnectionError)):
        return HTTPException(status_code=503, detail="AI service temporarily unavailable. Try again later.")
    return HTTPException(status_code=500, detail=str(e))


# ── Topic Card Generator (Stateless 4-Part AI Response) ────────

@router.post("/generate", response_model=TopicGenerateResponse)
@limiter.limit("30/minute")
async def generate_topic_card(request: Request, req: TopicGenerateRequest):
    """Generate a 4-part argument card for a topic. No difficulty, no scoring."""
    try:
        # 1. Fetch Topic Name
        topic_service = get_topic_service()
        topic = topic_service.get_topic(topic_id=req.topicId)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # 2. Fetch Study Materials (Context)
        material_service = get_material_service()
        materials = material_service.get_materials_by_topic(topic_id=req.topicId)
        
        study_materials_text = ""
        if materials:
            study_materials_text = (
                f"Main Arguments: {materials.main_arguments}\n"
                f"Counter Arguments: {materials.counter_arguments}\n"
                f"Rebuttals: {materials.rebuttals}"
            )

        # 3. Call AI Service (Stateless)
        service = get_ai_service()
        result = service.generate_topic_card(
            topic=topic.topic_name,
            topic_id=req.topicId,
            message=req.message,
            user_id=req.userId,
            study_materials=study_materials_text if study_materials_text else None
        )
        return result
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_materials_background(user_id: int, topic_id: int, topic_name: str, description: str):
    """Background task to generate materials for a new topic."""
    try:
        material_service = get_material_service()
        material_service.generate_and_save_materials(
            user_id=user_id,
            topic_id=topic_id,
            topic_name=topic_name,
            description=description or "",
            difficulty=3  # Default difficulty for auto-generation
        )
        logger.info(f"Auto-generated materials for topic {topic_id}")
    except Exception as e:
        logger.error(f"Failed to auto-generate materials for topic {topic_id}: {e}")


@router.post("", response_model=TopicResponse)
async def create_topic(topic: TopicCreate, background_tasks: BackgroundTasks):
    try:
        service = get_topic_service()
        created_topic = service.create_topic(
            user_id=topic.user_id,
            category_id=topic.category_id,
            topic_name=topic.topic_name,
            description=topic.description
        )
        
        # Auto-generate materials in background (non-blocking)
        background_tasks.add_task(
            _generate_materials_background,
            user_id=topic.user_id,
            topic_id=created_topic.topic_id,
            topic_name=topic.topic_name,
            description=topic.description or ""
        )
        
        return created_topic
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category_id}", response_model=List[TopicResponse])
async def get_topics_by_category(category_id: int):
    try:
        service = get_topic_service()
        return service.get_topics_by_category(category_id=category_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[TopicResponse])
async def get_topics_by_user(user_id: int):
    """Get all topics for a user, including uncategorized ones."""
    try:
        service = get_topic_service()
        return service.get_topics_by_user(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int):
    try:
        service = get_topic_service()
        topic = service.get_topic(topic_id=topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}")
async def delete_topic(topic_id: int):
    try:
        topic_service = get_topic_service()
        material_service = get_material_service()
        
        material_service.delete_materials(topic_id=topic_id)
        
        success = topic_service.delete_topic(topic_id=topic_id)
        if not success:
            raise HTTPException(status_code=404, detail="Topic not found")
        return {"message": "Topic deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/generate-materials", response_model=MaterialResponse)
async def generate_materials(topic_id: int, request: MaterialGenerate):
    try:
        topic_service = get_topic_service()
        topic = topic_service.get_topic(topic_id=topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        material_service = get_material_service()
        return material_service.generate_and_save_materials(
            user_id=request.user_id,
            topic_id=topic_id,
            topic_name=request.topic_name,
            description=request.description,
            difficulty=request.difficulty
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}/materials", response_model=MaterialResponse)
async def get_materials(topic_id: int):
    try:
        service = get_material_service()
        materials = service.get_materials_by_topic(topic_id=topic_id)
        if not materials:
            raise HTTPException(status_code=404, detail="No materials found for this topic")
        return materials
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
