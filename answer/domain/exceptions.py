class InsufficientCoinError(Exception):
    """Raised when user doesn't have enough coins to submit an answer"""
    def __init__(self, message="Insufficient coins to submit answer"):
        self.message = message
        super().__init__(self.message)
