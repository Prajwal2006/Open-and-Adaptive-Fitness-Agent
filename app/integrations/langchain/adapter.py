class LangChainAdapter:
    def is_available(self) -> bool:
        return False

    def get_tools(self) -> list:
        return []

    def create_chain(self) -> None:
        raise NotImplementedError("LangChain integration is not yet implemented.")
