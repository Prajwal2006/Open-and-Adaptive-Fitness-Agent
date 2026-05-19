from __future__ import annotations

from typing import Any


def safe_agent_response(kind: str, payload: dict[str, Any], status: str = "ok") -> dict[str, Any]:
    return {
        "type": kind,
        "status": status,
        "payload": payload,
        "orchestrator_safe": True,
    }


def compact_error(code: str, message: str) -> dict[str, Any]:
    return {
        "type": "error",
        "status": "error",
        "payload": {"code": code, "message": message},
        "orchestrator_safe": True,
    }
