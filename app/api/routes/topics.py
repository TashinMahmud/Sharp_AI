from fastapi import APIRouter, HTTPException
from typing import List

from app.models.topic import TopicCreate, TopicResponse
from app.models.material import MaterialGenerate, MaterialResponse
from app.services.topic_service import get_topic_service
from app.services.material_service import get_material_service

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("", response_model=TopicResponse)
async def create_topic(topic: TopicCreate):
    try:
        service = get_topic_service()
        return service.create_topic(
            user_id=topic.user_id,
            category_id=topic.category_id,
            topic_name=topic.topic_name,
            description=topic.description
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category_id}", response_model=List[TopicResponse])
async def get_topics_by_category(category_id: str):
    try:
        service = get_topic_service()
        return service.get_topics_by_category(category_id=category_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str):
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
async def delete_topic(topic_id: str):
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
async def generate_materials(topic_id: str, request: MaterialGenerate):
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
async def get_materials(topic_id: str):
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
