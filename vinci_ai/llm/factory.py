class Robot:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.history = []