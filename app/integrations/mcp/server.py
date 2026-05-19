from __future__ import annotations

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.mcp import tools

ToolFn = Callable[..., Awaitable[dict] | Awaitable[list[dict]]]


class MCPServer:
    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {
            "get_today_workout": tools.get_today_workout,
            "get_training_state": tools.get_training_state,
            "get_notifications": tools.get_notifications,
            "generate_workout_plan": tools.generate_workout_plan,
            "get_recovery_recommendation": tools.get_recovery_recommendation,
            "log_workout": tools.log_workout,
            "log_habit": tools.log_habit,
        }

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    async def run_tool(self, name: str, db: AsyncSession, **kwargs):
        if name not in self._tools:
            raise ValueError(f"Unknown MCP tool: {name}")
        return await self._tools[name](db, **kwargs)
