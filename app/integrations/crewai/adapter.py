class CrewAIAdapter:
    def is_available(self) -> bool:
        return False

    def get_agent(self) -> None:
        raise NotImplementedError("CrewAI integration is not yet implemented.")

    def create_crew(self) -> None:
        raise NotImplementedError("CrewAI integration is not yet implemented.")
