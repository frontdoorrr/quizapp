from dependency_injector import containers, providers

from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository
from game.application.game_service import GameService
from game.infra.repository.game_repo import GameRepository
from answer.application.answer_service import AnswerService
from answer.infra.repository.answer_repo import AnswerRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "user.interface.controllers",
            "user.application",
            "game.interface.controllers",
            "game.application",
            "answer.interface.controllers",
            "answer.application",
        ],
    )

    # User
    user_repo = providers.Singleton(UserRepository)
    user_service = providers.Singleton(UserService, user_repo=user_repo)

    # Game
    game_repo = providers.Singleton(GameRepository)
    game_service = providers.Singleton(GameService, game_repo=game_repo)

    # Answer
    answer_repo = providers.Singleton(AnswerRepository)
    answer_service = providers.Singleton(
        AnswerService, answer_repo=answer_repo, game_repo=game_repo
    )
