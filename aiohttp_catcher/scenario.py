from typing import Any, Awaitable, Callable, Dict, List, Type, Union
from inspect import isawaitable, iscoroutine, iscoroutinefunction

from aiohttp.web import Request


def is_async(f):
    return isawaitable(f) or iscoroutine(f) or iscoroutinefunction(f)


class Scenario:
    status_code: int = 500
    is_callable: bool = False
    stringify_exception: bool = False
    additional_fields: Union[Dict, Callable, Awaitable] = None

    def __init__(self, exceptions: List[Type[Exception]], func: Union[Callable, Awaitable] = None,
                 constant: Any = "Internal server error", stringify_exception: bool = False, status_code: int = 500,
                 additional_fields: Union[Dict, Callable, Awaitable] = None):
        self.exceptions = exceptions
        self.stringify_exception = stringify_exception
        self.func = func
        self.constant = constant
        self.additional_fields = additional_fields
        if not stringify_exception:
            if func and hasattr(func, "__call__"):
                self.is_callable = True
        self.status_code = status_code

    async def get_response_message(self, exc: Exception, request: Request) -> Any:
        if self.is_callable:
            if is_async(self.func):
                return await self.func(exc, request)
            return self.func(exc, request)
        if self.stringify_exception:
            return str(exc)
        return self.constant

    async def get_additional_fields(self, exc: Exception, req: Request) -> Dict:
        if not self.additional_fields:
            return {}
        if isinstance(self.additional_fields, Dict):
            return self.additional_fields
        if is_async(self.additional_fields):
            return await self.additional_fields(exc, req)
        return self.additional_fields(exc, req)

    def with_status_code(self, status_code) -> "Scenario":
        self.status_code = status_code
        return self

    def with_additional_fields(self, additional_fields: Union[Dict, Callable, Awaitable]) -> "Scenario":
        self.additional_fields = additional_fields
        return self

    def and_stringify(self) -> "Scenario":
        self.stringify_exception = True
        return self

    def and_return(self, constant: Any) -> "Scenario":
        self.constant = constant
        return self

    def and_call(self, func: Callable) -> "Scenario":
        self.is_callable = True
        self.func = func
        return self


def catch(*exceptions: Type[Exception]) -> Scenario:
    return Scenario(exceptions=list(exceptions))
