from dependency_injector import containers, providers

from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository
from user.infra.repository.user_repo import LoginHistoryRepository
from user.infra.repository.coin_repo import CoinWalletRepository, CoinRepository
from user.application.coin_service import CoinService
from game.application.game_service import GameService
from game.infra.repository.game_repo import GameRepository
from answer.application.answer_service import AnswerService
from answer.infra.repository.answer_repo import AnswerRepository
from inquiry.application.inquiry_service import InquiryService
from inquiry.infra.repository.inquiry_repo import InquiryRepository
from common.redis.client import RedisClient
from common.redis.config import RedisSettings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "user.interface.controllers",
            "user.application",
            "game.interface.controllers",
            "game.application",
            "answer.interface.controllers",
            "answer.application",
            "inquiry.interface.controllers",
            "inquiry.application",
        ],
    )

    # User
    user_repo = providers.Singleton(UserRepository)
    login_history_repo = providers.Singleton(LoginHistoryRepository)
    user_service = providers.Singleton(
        UserService,
        user_repo=user_repo,
        login_history_repo=login_history_repo,
    )

    # CoinWallet
    coin_wallet_repo = providers.Singleton(CoinWalletRepository)
    coin_repo = providers.Singleton(CoinRepository)
    coin_service = providers.Factory(
        CoinService,
        wallet_repository=coin_wallet_repo,
        coin_repository=coin_repo,
    )

    # Game
    game_repo = providers.Singleton(GameRepository)
    redis_settings = providers.Singleton(RedisSettings)
    redis_client = providers.Singleton(RedisClient, settings=redis_settings)
    game_service = providers.Factory(
        GameService, game_repo=game_repo, redis_client=redis_client
    )

    # Answer
    answer_repo = providers.Singleton(AnswerRepository)
    answer_service = providers.Singleton(
        AnswerService,
        answer_repo=answer_repo,
        game_repo=game_repo,
        user_repo=user_repo,
    )

    # Inquiry
    inquiry_repo = providers.Singleton(InquiryRepository)
    inquiry_service = providers.Singleton(
        InquiryService,
        inquiry_repo=inquiry_repo,
    )
