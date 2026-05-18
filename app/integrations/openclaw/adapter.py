class OpenClawAdapter:
    def is_available(self) -> bool:
        return False

    def connect(self) -> None:
        raise NotImplementedError("OpenClaw integration is not yet implemented.")

    def send_event(self, event: dict) -> None:
        raise NotImplementedError("OpenClaw integration is not yet implemented.")

    def get_tools(self) -> list:
        return []
