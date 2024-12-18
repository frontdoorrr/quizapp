from dependency_injector import containers, providers

from game.application.game_service import GameService
from game.infra.repository.game_repo import GameRepository
from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "user.interface.controllers",
            "user.application",
            "game.interface.controllers",
            "game.application",
        ],
    )

    user_repo = providers.Singleton(UserRepository)
    game_repo = providers.Singleton(GameRepository)
    user_service = providers.Singleton(UserService, user_repo=user_repo)
    game_service = providers.Singleton(GameService, game_repo=game_repo)
