# aiohttp-catcher


<div align="center">
    <a href="https://github.com/yuvalherziger/aiohttp-catcher/actions?query=workflow%3ACI"><img alt="CI Job" src="https://github.com/yuvalherziger/aiohttp-catcher/workflows/CI/badge.svg"></a>
    <a href="https://pypi.org/project/aiohttp-catcher"><img src="https://badge.fury.io/py/aiohttp-catcher.svg" alt="PyPI version" height="18"></a>
</div>

aiohttp-catcher is a centralized error handler for [aiohttp servers](https://docs.aiohttp.org/en/stable/web.html).
It enables consistant error handlling across your web server or API, so your code can raise Python exceptions that
will be handled however you want them to.

***

- [Quickstart](#quickstart)
- [Key Features](#key-features)
  * [Return a Constant](#return-a-constant)
  * [Stringify the Exception](#stringify-the-exception)
  * [Callables and Awaitables](#callables-and-awaitables)
  * [Handle Several Exceptions Similarly](#handle-several-exceptions-similarly)
  * [Scenarios as Dictionaries](#scenarios-as-dictionaries)
- [Development](#development)

***

## Quickstart

```python
from aiohttp import web
from aiohttp_catcher import catch, Catcher

async def hello(request):
    division = 1 / 0
    return web.Response(text=f"1 / 0 = {division}")


async def main():
    # Add a catcher:
    catcher = Catcher()

    # Register error-handling scenarios:
    await catcher.add_scenario(
        catch(ZeroDivisionError).with_status_code(400).and_return("Zero division makes zero sense")
    )

    # Register your catcher as an aiohttp middleware:
    app = web.Application(middlewares=[catcher.middleware])
    app.add_routes([web.get("/divide-by-zero", hello)])
    web.run_app(app)
```

Making a request to `/divide-by-zero` will return a 400 status code with the following body:
```json
{"code": 400, "message": "Zero division makes zero sense"}
```

***

## Key Features

### Return a Constant

In case you want some exceptions to return a constant message across your application, you can do
so by using the `.and_return("some value")` method:

```python
await catcher.add_scenario(
    catch(ZeroDivisionError).with_status_code(400).and_return("Zero division makes zero sense")
)
```

***

### Stringify the Exception

In some cases, you would want to return a stringified version of your exception, should it entail
user-friendly information.

```
class EntityNotFound(Exception):
    def __init__(self, entity_id, *args, **kwargs):
        super(EntityNotFound, self).__init__(*args, **kwargs)
        self.entity_id = entity_id

    def __str__(self):
        return f"Entity {self.entity_id} could not be found"


@routes.get("/user/{user_id}")
async def get_user(request):
    user_id = request.match_info.get("user_id")
    if user_id not in user_db:
        raise EntityNotFound(entity_id=user_id)
    return user_db[user_id]

# Your catcher can be directed to stringify particular exceptions:

await catcher.add_scenario(
    catch(EntityNotFound).with_status_code(404).and_stringify()
)
```

***

### Callables and Awaitables

In some cases, you'd want the message returned by your server for some exceptions to call a custom
function.  This function can either be a synchronous function or an awaitable one.  It should expect
a single argument, which is the exception being raised:

```python
# Can be a synchronous function as well:
async def write_message(exc: Exception):
    return "Whoops"

await catcher.add_scenarios(
    catch(MyCustomException2).with_status_code(401).and_call(write_message),
    catch(MyCustomException2).with_status_code(403).and_call(lambda exc: str(exc))
)

```

***

### Handle Several Exceptions Similarly

You can handle several exceptions in the same manner by adding them to the same scenario:

```python
await catcher.add_scenario(
    catch(
        MyCustomException1,
        MyCustomException2,
        MyCustomException3
    ).with_status_code(418).and_return("User-friendly error message")
)
```

***

### Scenarios as Dictionaries

You can register your scenarios as dictionaries as well:

```python
await catcher.add_scenarios(
    {
        "exceptions": [ZeroDivisionError],
        "constant": "Zero division makes zero sense",
        "status_code": 400,
    },
    {
        "exceptions": [EntityNotFound],
        "stringify_exception": True,
        "status_code": 404,
    },
    {
        "exceptions": [IndexError],
        "func": lambda exc: f"Out of bound: {str(exc)}",
        "status_code": 418,
    },
)
```

***

## Development

Contributions are warmly welcomed.  Before submitting your PR, please run the tests using the following Make target:

```bash
make ci
```

Alternatively, you can run each test suite separately:

1. Unit tests:

   ```bash
   make test/py
   ```

2. Linting with pylint:

   ```bash
   make pylint
   ```

3. Static security checks with bandit:

   ```bash
   make pybandit
   ```
