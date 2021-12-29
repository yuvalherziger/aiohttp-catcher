from typing import Callable, Dict, List
import logging

from aiohttp.typedefs import Handler, Request
from aiohttp.web import middleware

from aiohttp_catcher.scenario import Scenario

LOGGER = logging.getLogger(__name__)


class Catcher:
    scenarios: List[Scenario] = []
    scenario_map: Dict
    envelope = "message"
    code = "code"

    def __init__(self, scenarios: List[Scenario] = None, envelope: str = "message", code: str = "code"):
        pass

    def register_scenario(self, scenario: Scenario):
        exceptions = scenario.exceptions
        for exc in exceptions:
            exc_module = f"{exc.__module__}.{Exception.__name__}"
            if exc_module in self.scenario_map:
                LOGGER.warning("A new handler for <%s> has been registered.  It will override existing handlers",
                               exc_module)
            self.scenario_map[exc_module] = scenario

    @property
    def middleware(self) -> Callable:

        @middleware
        async def catcher_middleware(request: Request, handler: Handler):
            try:
                return await handler(request)
            except Exception as exc:
                exc_module = f"{exc.__class__.__module__}.{exc.__class__.__name__}"
                if exc_module in self.scenario_map:
                    # TODO: implement handler
                    pass

        return catcher_middleware
