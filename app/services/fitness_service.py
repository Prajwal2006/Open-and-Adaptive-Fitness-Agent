from sqlalchemy.ext.asyncio import AsyncSession
from app.core.orchestration_bridge.bridge import OrchestrationBridge
from app.core.recommendation_engine.engine import RecommendationEngine
from app.core.recovery_engine.engine import RecoveryEngine


class FitnessService:
    def __init__(self):
        self.bridge = OrchestrationBridge()
        self.recommender = RecommendationEngine()
        self.recovery = RecoveryEngine()

    async def get_full_context(self, db: AsyncSession) -> dict:
        return await self.bridge.get_agent_context(db)

    async def run_daily_update(self, db: AsyncSession) -> dict:
        await self.recovery.update_readiness_snapshot(db)
        recs = await self.recommender.generate_recommendations(db)
        if recs:
            await self.recommender.save_recommendations(recs, db)
        return {"readiness_updated": True, "recommendations_generated": len(recs)}
