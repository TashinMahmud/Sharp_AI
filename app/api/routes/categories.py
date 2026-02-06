from fastapi import APIRouter, HTTPException
from typing import List

from app.models.category import CategoryCreate, CategoryResponse
from app.services.category_service import get_category_service

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
async def get_categories(user_id: str):
    try:
        service = get_category_service()
        return service.get_categories(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(category_id: str):
    try:
        service = get_category_service()
        success = service.delete_category(category_id=category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
