from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_session
from app.schemas.schemas import ProgressSummaryResponse
from app.core.orchestration_bridge.bridge import OrchestrationBridge

router = APIRouter()
bridge = OrchestrationBridge()


@router.get("/progress-summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(db: AsyncSession = Depends(get_db_session)):
    data = await bridge.get_progress_response(db)
    return ProgressSummaryResponse(**data)
