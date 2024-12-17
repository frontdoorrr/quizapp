from dependency_injector import containers, providers

from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "user.interface.controllers",
            "user.application",
        ],
    )

    user_repo = providers.Singleton(UserRepository)
    user_service = providers.Singleton(UserService, user_repo=user_repo)
