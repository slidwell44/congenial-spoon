from person_tool.factories.service_factory import service_factory


class SystemApplication:
    def __init__(self) -> None:
        self.service_factory = service_factory

    async def check_system_readiness(self) -> bool:
        async with self.service_factory(use_transaction=False) as sf:
            check: bool = await sf.system_service.check_system_readiness()
        return check
