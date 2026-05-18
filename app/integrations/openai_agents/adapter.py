class OpenAIAgentsAdapter:
    def is_available(self) -> bool:
        return False

    def get_tools(self) -> list:
        return []

    def create_agent(self) -> None:
        raise NotImplementedError("OpenAI Agents integration is not yet implemented.")
