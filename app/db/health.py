from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_database_health(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("SELECT 1"))
        _ = result.scalar_one()
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
