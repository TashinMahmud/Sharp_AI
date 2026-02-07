from fastapi import APIRouter, HTTPException

from app.services.category_service import get_category_service
from app.services.topic_service import get_topic_service
from app.services.material_service import get_material_service
from app.services.progress_service import get_progress_service

router = APIRouter(prefix="/users", tags=["users"])


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    try:
        category_service = get_category_service()
        topic_service = get_topic_service()
        material_service = get_material_service()
        progress_service = get_progress_service()
        
        deleted_categories = 0
        deleted_topics = 0
        deleted_materials = 0
        
        # 1. Get all categories for this user
        categories = category_service.get_categories(user_id=user_id)
        
        for category in categories:
            # 2. Get all topics in this category
            topics = topic_service.get_topics_by_category(category_id=category.category_id)
            
            for topic in topics:
                # 3. Delete materials for each topic
                if material_service.delete_materials(topic_id=topic.topic_id):
                    deleted_materials += 1
                # 4. Delete the topic
                if topic_service.delete_topic(topic_id=topic.topic_id):
                    deleted_topics += 1
            
            # 5. Delete the category
            if category_service.delete_category(category_id=category.category_id):
                deleted_categories += 1
        
        # 6. Delete user progress/stats
        deleted_progress = progress_service.delete_user_progress(user_id=user_id)
        
        return {
            "message": "User data deleted successfully",
            "deleted": {
                "categories": deleted_categories,
                "topics": deleted_topics,
                "materials": deleted_materials,
                "progress_records": deleted_progress
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
