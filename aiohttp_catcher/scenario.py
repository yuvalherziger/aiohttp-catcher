from typing import Callable, List, Any


class Scenario:
    status_code: int = 500
    is_callable: bool = False
    stringify_exception: bool = False

    def __init__(self, exceptions: List[Exception], func: Callable = None, constant: Any = None,
                 stringify_exception: bool = False, status_code: int = 500):
        self.exceptions = exceptions
        self.stringify_exception = stringify_exception
        self.func = func
        self.constant = constant
        if not stringify_exception:
            if func and hasattr(func, "__call__"):
                self.is_callable = True
        self.status_code = status_code

    async def respond(self, exc: Exception) -> Any:
        if self.is_callable:
            return self.func(exc)
        elif self.stringify_exception:
            return str(exc)
        return self.constant

    def with_status_code(self, status_code) -> "Scenario":
        self.status_code = status_code
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


def catch(*exceptions: Exception) -> Scenario:
    return Scenario(exceptions=list(exceptions))
