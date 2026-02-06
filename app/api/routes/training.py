from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Literal
import random

from openai import APIError, APIConnectionError, AuthenticationError, RateLimitError

from app.core.limiter import limiter
from app.services.material_service import get_material_service
from app.services.topic_service import get_topic_service
from app.services.ai_service import get_ai_service
from app.services.progress_service import get_progress_service
from app.models.progress import ProgressCreate, ProgressStats
from app.schemas import (
    DebateChatResponse,
    EvaluateRequest,
    EvaluateResponse,
    HintRequest,
    HintResponse,
)

router = APIRouter(prefix="/training", tags=["training"])


def _handle_ai_errors(e: Exception) -> HTTPException:
    if isinstance(e, RateLimitError):
        return HTTPException(status_code=429, detail="AI rate limit exceeded. Try again shortly.")
    if isinstance(e, AuthenticationError):
        return HTTPException(status_code=401, detail="Invalid AI API key.")
    if isinstance(e, (APIError, APIConnectionError)):
        return HTTPException(status_code=503, detail="AI service temporarily unavailable. Try again later.")
    return HTTPException(status_code=500, detail=str(e))


class RandomQuizRequest(BaseModel):
    user_id: str
    difficulty: str = "medium"


class CategoryQuizRequest(BaseModel):
    user_id: str
    category_id: str
    difficulty: str = "medium"


class TopicQuizRequest(BaseModel):
    user_id: str
    topic_id: str
    difficulty: str = "medium"


class TopicDebateRequest(BaseModel):
    user_id: str
    session_id: str
    topic_id: str
    difficulty: str = "medium"
    role: Literal["user_argument", "user_counter", "user_rebuttal"]
    message: str


@router.post("/debate", response_model=DebateChatResponse)
@limiter.limit("30/minute")
async def start_topic_debate(request: Request, req: TopicDebateRequest):
    try:
        # 1. Fetch Topic Name
        topic_service = get_topic_service()
        topic = topic_service.get_topic(topic_id=req.topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # 2. Fetch Study Materials (Context)
        material_service = get_material_service()
        materials = material_service.get_materials_by_topic(topic_id=req.topic_id)
        
        study_materials_text = ""
        if materials:
            study_materials_text = (
                f"Main Arguments: {materials.main_arguments}\n"
                f"Counter Arguments: {materials.counter_arguments}\n"
                f"Rebuttals: {materials.rebuttals}"
            )

        # 3. Call AI Service with Context
        service = get_ai_service()
        result = service.debate_chat(
            topic=topic.topic_name,
            difficulty=req.difficulty,
            role=req.role,
            message=req.message,
            user_id=req.user_id,
            session_id=req.session_id,
            study_materials=study_materials_text if study_materials_text else None
        )
        return result
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hint", response_model=HintResponse)
@limiter.limit("30/minute")
def generate_hint(request: Request, req: HintRequest):
    try:
        service = get_ai_service()
        return service.generate_hint(req.question, req.arguments)
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e


@router.post("/evaluate", response_model=EvaluateResponse)
@limiter.limit("30/minute")
def evaluate_answer(request: Request, req: EvaluateRequest):
    try:
        service = get_ai_service()
        evaluation = service.evaluate_answer(
            req.question,
            req.selected_answer,
            req.correct_answer,
            req.difficulty,
        )
        
        # Save Progress if user_id and topic_id are provided
        if req.user_id and req.topic_id:
            try:
                # Simple case-insensitive check for correctness
                is_correct = req.selected_answer.strip().lower() == req.correct_answer.strip().lower()
                
                progress_service = get_progress_service()
                progress_service.save_quiz_result(ProgressCreate(
                    user_id=req.user_id,
                    topic_id=req.topic_id,
                    topic_name=req.topic_name or "Unknown Topic",
                    score=1 if is_correct else 0,
                    difficulty=req.difficulty
                ))
            except Exception as e:
                # Don't fail the request if saving stats fails
                print(f"Failed to save progress: {e}")
                
        return evaluation
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e


@router.get("/stats/{user_id}", response_model=ProgressStats)
@limiter.limit("60/minute")
def get_user_stats(request: Request, user_id: str):
    try:
        service = get_progress_service()
        return service.get_user_stats(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/random-quiz")
async def random_quiz(request: RandomQuizRequest):
    try:
        material_service = get_material_service()
        
        all_materials = material_service.vector_db.get(
            where={
                "$and": [
                    {"user_id": {"$eq": request.user_id}},
                    {"type": {"$eq": "material"}}
                ]
            },
            include=["metadatas"]
        )
        
        if not all_materials or not all_materials["metadatas"]:
            raise HTTPException(status_code=404, detail="No training materials found. Please generate materials for your topics first.")
        
        random_material = random.choice(all_materials["metadatas"])
        
        arguments = eval(random_material["main_arguments"])
        
        ai_service = get_ai_service()
        quiz = ai_service.generate_quiz(
            topic=random_material["topic_name"],
            difficulty=request.difficulty,
            arguments=arguments
        )
        
        quiz["topic_id"] = random_material["topic_id"]
        quiz["topic_name"] = random_material["topic_name"]
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/category-quiz")
async def category_quiz(request: CategoryQuizRequest):
    try:
        topic_service = get_topic_service()
        topics = topic_service.get_topics_by_category(category_id=request.category_id)
        
        if not topics:
            raise HTTPException(status_code=404, detail="No topics found in this category")
        
        topic_ids = [topic.topic_id for topic in topics]
        
        material_service = get_material_service()
        category_materials = []
        
        for topic_id in topic_ids:
            material = material_service.get_materials_by_topic(topic_id=topic_id)
            if material:
                category_materials.append({
                    "topic_id": topic_id,
                    "topic_name": next(t.topic_name for t in topics if t.topic_id == topic_id),
                    "arguments": material.main_arguments
                })
        
        if not category_materials:
            raise HTTPException(status_code=404, detail="No training materials found for topics in this category")
        
        selected = random.choice(category_materials)
        
        ai_service = get_ai_service()
        quiz = ai_service.generate_quiz(
            topic=selected["topic_name"],
            difficulty=request.difficulty,
            arguments=selected["arguments"]
        )
        
        quiz["topic_id"] = selected["topic_id"]
        quiz["topic_name"] = selected["topic_name"]
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topic-quiz")
async def topic_quiz(request: TopicQuizRequest):
    try:
        material_service = get_material_service()
        materials = material_service.get_materials_by_topic(topic_id=request.topic_id)
        
        if not materials:
            raise HTTPException(status_code=404, detail="No materials found for this topic. Generate materials first.")
        
        topic_service = get_topic_service()
        topic = topic_service.get_topic(topic_id=request.topic_id)
        
        ai_service = get_ai_service()
        quiz = ai_service.generate_quiz(
            topic=topic.topic_name if topic else "Unknown Topic",
            difficulty=request.difficulty,
            arguments=materials.main_arguments
        )
        
        quiz["topic_id"] = request.topic_id
        quiz["topic_name"] = topic.topic_name if topic else "Unknown Topic"
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
