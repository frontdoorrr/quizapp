class WalletNotFoundError(Exception):
    def __init__(self, wallet_id: str):
        self.wallet_id = wallet_id
        super().__init__(f"Wallet not found: {wallet_id}")


class UserWalletNotFoundError(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"Wallet not found for user: {user_id}")


class InsufficientCoinsError(Exception):
    def __init__(self, wallet_id: str, required: int, available: int):
        self.wallet_id = wallet_id
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient coins in wallet {wallet_id}: required {required}, available {available}"
        )


class MaxBalanceExceededError(Exception):
    def __init__(self, wallet_id: str, max_balance: int):
        self.wallet_id = wallet_id
        self.max_balance = max_balance
        super().__init__(
            f"Adding coin would exceed maximum balance of {max_balance} for wallet {wallet_id}"
        )
