# aiohttp-catcher

<div align="left">
  <a href="https://github.com/yuvalherziger/aiohttp-catcher/actions?query=workflow%3ACI"><img alt="CI Job" src="https://github.com/yuvalherziger/aiohttp-catcher/workflows/CI/badge.svg"></a>
  <a href="https://pypi.org/project/aiohttp-catcher"><img src="https://badge.fury.io/py/aiohttp-catcher.svg" alt="PyPI version" height="18"></a>
</div>

aiohttp-catcher is a centralized error handler for [aiohttp servers](https://docs.aiohttp.org/en/stable/web.html).
It enables consistent error handling across your web server or API, so your code can raise Python exceptions that
will be mapped to consistent, user-friendly error messages.

***

- [Quickstart](#quickstart)
- [What's New in 0.3.0?](#what-s-new-in-030-)
- [Key Features](#key-features)
  * [Return a Constant](#return-a-constant)
  * [Stringify the Exception](#stringify-the-exception)
  * [Canned HTTP 4xx and 5xx Errors (aiohttp Exceptions)](#canned-http-4xx-and-5xx-errors--aiohttp-exceptions-)
  * [Callables and Awaitables](#callables-and-awaitables)
  * [Handle Several Exceptions Similarly](#handle-several-exceptions-similarly)
  * [Scenarios as Dictionaries](#scenarios-as-dictionaries)
  * [Additional Fields](#additional-fields)
  * [Default for Unhandled Exceptions](#default-for-unhandled-exceptions)
- [Development](#development)

***

## Quickstart

Install aiohttp-catcher:

```shell
pip install aiohttp-catcher
```

Start catching errors in your aiohttp-based web server:

```python
from aiohttp import web
from aiohttp_catcher import catch, Catcher

async def divide(request):
  quotient = 1 / 0
  return web.Response(text=f"1 / 0 = {quotient}")


async def main():
  # Add a catcher:
  catcher = Catcher()

  # Register error-handling scenarios:
  await catcher.add_scenario(
    catch(ZeroDivisionError).with_status_code(400).and_return("Zero division makes zero sense")
  )

  # Register your catcher as an aiohttp middleware:
  app = web.Application(middlewares=[catcher.middleware])
  app.add_routes([web.get("/divide-by-zero", divide)])
  web.run_app(app)
```

Making a request to `/divide-by-zero` will return a 400 status code with the following body:
```json
{"code": 400, "message": "Zero division makes zero sense"}
```

***

## What's New in 0.3.0?

* **Canned Scenarios:** You can now use a [canned list of scenarios](#canned-http-4xx-and-5xx-errors--aiohttp-exceptions-),
  capturing all of [aiohttp's web exceptions](https://docs.aiohttp.org/en/latest/web_exceptions.html) out of the box.
* **More flexible Callables and Awaitables:** Callables and Awaitables are now invoked with a second argument,  
  the aiohttp `Request` instance, to add more flexibility to custom messages.

***

## Key Features

### Return a Constant

In case you want some exceptions to return a constant message across your application, you can do
so by using the `and_return("some value")` method:

```python
await catcher.add_scenario(
  catch(ZeroDivisionError).with_status_code(400).and_return("Zero division makes zero sense")
)
```

***

### Stringify the Exception

In some cases, you would want to return a stringified version of your exception, should it entail
user-friendly information.

```python
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

### Canned HTTP 4xx and 5xx Errors (aiohttp Exceptions)

As of version [0.3.0](https://github.com/yuvalherziger/aiohttp-catcher/releases/tag/0.3.0), you
can register [all of aiohttp's web exceptions](https://docs.aiohttp.org/en/latest/web_exceptions.html).
This is particularly useful when you want to ensure all possible HTTP errors are handled consistently.

Register the canned HTTP errors in the following way:

```python
from aiohttp import web
from aiohttp_catcher import Catcher
from aiohttp_catcher.canned import AIOHTTP_SCENARIOS


async def main():
  # Add a catcher:
  catcher = Catcher()
  # Register aiohttp web errors:
  await catcher.add_scenario(*AIOHTTP_SCENARIOS)
  # Register your catcher as an aiohttp middleware:
  app = web.Application(middlewares=[catcher.middleware])
  web.run_app(app)
```

Once you've registered the canned errors, you can rely on aiohttp-catcher to convert errors raised by aiohttp
to user-friendly error messages.  For example, `curl`ing a non-existent route in your server will return the
following error out of the box:

```json
{"code": 404, "message": "HTTPNotFound"}
```

***

### Callables and Awaitables

In some cases, you'd want the message returned by your server for some exceptions to call a custom
function.  This function can either be a synchronous function or an awaitable one.  Your function should expect
two arguments:

1. The exception being raised by handlers.
2. The request object - an instance of `aiohttp.web.Request`.

```python
from aiohttp.web import Request
from aiohttp_catcher import catch, Catcher

# Can be a synchronous function:
async def write_message(exc: Exception, request: Request):
  return "Whoops"

catcher = Catcher()
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

### Additional Fields

You can enrich your error responses with additional fields. You can provide additional fields using
literal dictionaries or with callables.  Your function should expect two arguments:

1. The exception being raised by handlers.
2. The request object - an instance of `aiohttp.web.Request`.

```python
# Using a literal dictionary:
await catcher.add_scenario(
  catch(EntityNotFound).with_status_code(404).and_stringify().with_additional_fields({"error_code": "ENTITY_NOT_FOUND"})
)

# Using a function (or an async function):
await catcher.add_scenario(
  catch(EntityNotFound).with_status_code(404).and_stringify().with_additional_fields(
    lambda exc, req: {"error_code": e.error_code, "method": req.method}
  )
)
```

***

### Default for Unhandled Exceptions

Exceptions that aren't registered with scenarios in your `Catcher` will default to 500, with a payload similar to
the following:

```json
{"code": 500, "message": "Internal server error"}
```

***

## Development

Contributions are warmly welcomed.  Before submitting your PR, please run the tests using the following Make target:

```bash
make ci
```

Alternatively, you can run each test separately:

Unit tests:

```bash
make test/py
```

Linting with pylint:

```bash
make pylint
```

Static security checks with bandit:

```bash
make pybandit
```
