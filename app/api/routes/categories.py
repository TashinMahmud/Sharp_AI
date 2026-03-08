from fastapi import APIRouter, HTTPException
from typing import List

from app.models.category import CategoryCreate, CategoryResponse
from app.services.category_service import get_category_service
from app.services.topic_service import get_topic_service
from app.services.material_service import get_material_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    try:
        service = get_category_service()
        return service.create_category(
            user_id=category.user_id,
            category_name=category.category_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=List[CategoryResponse])
async def get_categories(user_id: int):
    try:
        service = get_category_service()
        return service.get_categories(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    try:
        category_service = get_category_service()
        topic_service = get_topic_service()
        material_service = get_material_service()
        
        # 1. Get all topics in this category
        topics = topic_service.get_topics_by_category(category_id=category_id)
        
        # 2. Delete materials and topics for each topic
        for topic in topics:
            material_service.delete_materials(topic_id=topic.topic_id)
            topic_service.delete_topic(topic_id=topic.topic_id)
        
        # 3. Delete the category itself
        success = category_service.delete_category(category_id=category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {
            "message": "Category and all related data deleted successfully",
            "topics_deleted": len(topics)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
