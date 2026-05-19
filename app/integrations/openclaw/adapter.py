from __future__ import annotations

from app.integrations.openclaw.responses import safe_agent_response
from app.integrations.openclaw.tool_schemas import OPENCLAW_TOOL_SCHEMAS


class OpenClawAdapter:
    def __init__(self) -> None:
        self._connected = False

    def is_available(self) -> bool:
        return True

    def connect(self) -> None:
        self._connected = True

    def send_event(self, event: dict) -> dict:
        if not self._connected:
            self.connect()
        return safe_agent_response("openclaw_event", {"event": event, "accepted": True})

    def get_tools(self) -> list:
        return OPENCLAW_TOOL_SCHEMAS
