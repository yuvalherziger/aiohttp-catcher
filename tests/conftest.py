from aiohttp import web
import pytest


class AppClientError(Exception):
    pass


class EntityNotFound(AppClientError):
    pass


class Forbidden(AppClientError):
    pass


@pytest.fixture
def app() -> web.Application:
    app = web.Application()
    return app

@pytest.fixture
def routes() -> web.RouteTableDef:
    router = web.RouteTableDef()

    @router.get("/divide")
    async def divide(request: web.Request):
        a = int(request.query.get("a"))
        b = int(request.query.get("b"))
        return web.json_response({"result": a / b})

    @router.get("/get-element-n")
    async def get_element_n(request: web.Request):
        rng = range(10)
        idx = int(request.query.get("n"))
        return web.json_response({"result": rng[idx]})

    @router.get("/user/{id}")
    async def get_user_by_id(request: web.Request):
        user_db = {
            "1000": {
                "name": "John Doe"
            },
            "1001": {
                "name": "Jayne Doe"
            },
        }
        user_id = request.match_info["id"]
        user = user_db.get(user_id)
        try:
            return web.json_response(user_db[user_id])
        except KeyError:
            raise EntityNotFound(f"User ID {user_id} could not be found")

    @router.get("/concat")
    async def concat(request: web.Request):
        a = request.query.get("a")
        b = request.query.get("b")
        return web.json_response({"result": a + b})

    return router
