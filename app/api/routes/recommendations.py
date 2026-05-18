from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.dependencies import get_db_session
from app.schemas.schemas import RecommendationResponse
from app.models.orm_models import Recommendation
from typing import List

router = APIRouter()


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(Recommendation).order_by(Recommendation.priority.desc(), Recommendation.created_at.desc())
    )
    recs = result.scalars().all()
    return [RecommendationResponse.model_validate(r) for r in recs]
