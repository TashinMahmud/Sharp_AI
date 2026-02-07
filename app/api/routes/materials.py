
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List


from app.services.material_service import get_material_service, MaterialService
from app.services.topic_service import get_topic_service, TopicService
from app.models.material import MaterialGenerate, MaterialResponse
from app.core.limiter import limiter
from fastapi import Request

router = APIRouter(prefix="/materials", tags=["materials"])

class GenerateMaterialRequest(BaseModel):
    topic_id: str
    user_id: str

@router.post("/generate", response_model=MaterialResponse)
@limiter.limit("5/minute")
def generate_materials(
    request: Request,
    req: GenerateMaterialRequest,
    service: MaterialService = Depends(get_material_service),
    topic_service: TopicService = Depends(get_topic_service)
):
    try:
        # Get topic details first
        topic = topic_service.get_topic(req.topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
            
        return service.generate_and_save_materials(
            user_id=req.user_id,
            topic_id=req.topic_id,
            topic_name=topic.topic_name,
            description=topic.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{topic_id}", response_model=Optional[MaterialResponse])
def get_materials(
    topic_id: str,
    service: MaterialService = Depends(get_material_service)
):
    material = service.get_materials_by_topic(topic_id)
    if not material:
        raise HTTPException(status_code=404, detail="Materials not found")
    return material
