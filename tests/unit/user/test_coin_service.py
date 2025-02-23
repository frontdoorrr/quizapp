import pytest
from datetime import datetime
from user.application.coin_service import CoinService
from user.domain.user import CoinWallet, CoinStatus
from user.domain.exceptions import WalletNotFoundError, MaxBalanceExceededError


class TestCoinService:
    @pytest.fixture
    def coin_service(self, mocker):
        self.wallet_repo = mocker.Mock()
        self.coin_repo = mocker.Mock()
        return CoinService(
            wallet_repository=self.wallet_repo, coin_repository=self.coin_repo
        )

    def test_create_wallet(self, coin_service):
        # Given
        user_id = "test-user-id"
        max_balance = 5
        self.wallet_repo.find_by_user_id.return_value = None

        # When
        wallet = coin_service.create_wallet(user_id, max_balance)

        # Then
        assert wallet.user_id == user_id
        assert wallet.max_balance == max_balance
        assert wallet.balance == 0

    def test_get_wallet(self, coin_service):
        # Given
        user_id = "test-user-id"
        mock_wallet = CoinWallet(
            id="test-wallet-id",
            user_id=user_id,
            balance=3,
            max_balance=5,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.wallet_repo.find_by_user_id.return_value = mock_wallet

        # When
        wallet = coin_service.get_wallet(user_id)

        # Then
        assert wallet.id == mock_wallet.id
        assert wallet.balance == mock_wallet.balance
