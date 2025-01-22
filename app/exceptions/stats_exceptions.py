class StatsError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Failed to generate statistics: {message}")


