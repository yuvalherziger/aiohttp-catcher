from typing import Callable, Dict, Union
import json
import logging

from aiohttp.typedefs import Handler
from aiohttp.web import json_response, middleware, Request

from aiohttp_catcher.scenario import Scenario

LOGGER = logging.getLogger(__name__)


async def get_full_class_name(cls: type) -> str:
    return f"{cls.__module__}.{cls.__name__}"


class Catcher:
    scenario_map: Dict = {}
    envelope: str
    code: str

    def __init__(self, envelope: str = "message", code: str = "code", encoder: Callable = json.dumps):
        self.envelope = envelope
        self.code = code
        self.encoder = encoder

    async def add_scenario(self, scenario: Union[Scenario, Dict]):
        if isinstance(scenario, Dict):
            scenario = Scenario(**scenario)

        exceptions = scenario.exceptions
        for exc in exceptions:
            exc_module = await get_full_class_name(exc)
            if exc_module in self.scenario_map:
                LOGGER.debug("A new handler for <%s> has been registered. It will override existing handlers",
                             exc_module)
            self.scenario_map[exc_module] = scenario

    async def add_scenarios(self, *scenarios: Union[Scenario, Dict]):
        for scenario in scenarios:
            await self.add_scenario(scenario)

    @property
    def middleware(self) -> Callable:

        @middleware
        async def catcher_middleware(request: Request, handler: Handler):
            try:
                return await handler(request)
            except Exception as exc:
                exc_module = await get_full_class_name(exc.__class__)
                scenario: Scenario
                if exc_module in self.scenario_map:
                    scenario = self.scenario_map[exc_module]
                else:
                    LOGGER.exception("aiohttp-catcher caught an unhandled exception")
                    scenario = Scenario(exceptions=[type(exc)])
                additional_fields: Dict = await scenario.get_additional_fields(exc=exc, req=request)
                data = {
                    self.envelope: await scenario.get_response_message(exc=exc, request=request),
                    self.code: scenario.status_code,
                    **additional_fields
                }
                return json_response(
                    data=data,
                    status=scenario.status_code,
                    dumps=self.encoder
                )
        return catcher_middleware
