from aiohttp import web

from aiohttp_catcher import catch, Catcher
from conftest import AppClientError, EntityNotFound
from dicttoxml import dicttoxml


class TestCatcher:

    @staticmethod
    async def test_return_constant_message(aiohttp_client, routes, loop):
        catcher = Catcher()
        await catcher.add_scenario(
            catch(ZeroDivisionError).with_status_code(403).and_return("Zero division makes zero sense")
        )

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/divide?a=10&b=2")
        assert 200 == resp.status
        assert 5 == (await resp.json()).get("result")

        resp = await client.get("/divide?a=10&b=0")
        assert 403 == resp.status
        assert "Zero division makes zero sense" == (await resp.json()).get("message")

    @staticmethod
    async def test_handle_single_scenario_and_multiple_exceptions(aiohttp_client, routes, loop):
        expected_message = "I'm a teapot"
        expected_code = 418
        catcher = Catcher()
        await catcher.add_scenario(
            catch(ZeroDivisionError, EntityNotFound, IndexError).with_status_code(expected_code).and_return(expected_message)
        )
        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/divide?a=10&b=0")
        assert expected_code == resp.status
        assert expected_message == (await resp.json()).get("message")

        resp = await client.get("/user/1009")
        assert expected_code == resp.status
        assert expected_message == (await resp.json()).get("message")

        resp = await client.get("/get-element-n?n=100")
        assert expected_code == resp.status
        assert expected_message == (await resp.json()).get("message")

    @staticmethod
    async def test_custom_encoder(aiohttp_client, routes, loop):
        expected_message = "I'm a teapot"
        expected_code = 418
        catcher = Catcher(encoder=lambda dict, *args, **kwargs: dicttoxml(dict).decode("utf-8"))
        await catcher.add_scenario(
            catch(ZeroDivisionError).with_status_code(expected_code).and_return(expected_message)
        )
        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/divide?a=10&b=0")
        assert expected_code == resp.status
        assert "teapot" in await resp.text()

    @staticmethod
    async def test_return_stringified_exception(aiohttp_client, routes, loop):
        catcher = Catcher()
        await catcher.add_scenario(
            catch(EntityNotFound).with_status_code(404).and_stringify()
        )

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/user/1001")
        assert 200 == resp.status
        assert "Jayne Doe" == (await resp.json()).get("name")

        resp = await client.get("/user/1009")
        assert 404 == resp.status
        assert "User ID 1009 could not be found" == (await resp.json()).get("message")

    @staticmethod
    async def test_invoke_blocking_callable(aiohttp_client, routes, loop):
        catcher = Catcher()
        await catcher.add_scenario(
            catch(EntityNotFound).with_status_code(404).and_stringify()
        )

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/user/1001")
        assert 200 == resp.status
        assert "Jayne Doe" == (await resp.json()).get("name")

        resp = await client.get("/user/1009")
        assert 404 == resp.status
        assert "User ID 1009 could not be found" == (await resp.json()).get("message")

    @staticmethod
    async def test_catch_parent_exception(aiohttp_client, routes, loop):
        catcher = Catcher()
        await catcher.add_scenario(
            catch(AppClientError).with_status_code(404).and_stringify()
        )

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/user/1001")
        assert 200 == resp.status
        assert "Jayne Doe" == (await resp.json()).get("name")

        resp = await client.get("/user/1009")
        assert 404 == resp.status
        assert "User ID 1009 could not be found" == (await resp.json()).get("message")

    @staticmethod
    async def test_invoke_callable(aiohttp_client, routes, loop):
        catcher = Catcher()
        await catcher.add_scenario(
            catch(IndexError).with_status_code(418).and_call(lambda exc: f"Out of bound: {str(exc)}")
        )

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/get-element-n?n=1")
        assert 200 == resp.status
        assert 1 == (await resp.json()).get("result")

        resp = await client.get("/get-element-n?n=100")
        assert 418 == resp.status
        assert "Out of bound: range object index out of range" == (await resp.json()).get("message")

    @staticmethod
    async def test_invoke_awaitable(aiohttp_client, routes, loop):
        catcher = Catcher()

        async def async_callable(exc):
            return f"Out of bound: {str(exc)}"

        await catcher.add_scenario(
            catch(IndexError).with_status_code(418).and_call(async_callable)
        )

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/get-element-n?n=1")
        assert 200 == resp.status
        assert 1 == (await resp.json()).get("result")

        resp = await client.get("/get-element-n?n=100")
        assert 418 == resp.status
        assert "Out of bound: range object index out of range" == (await resp.json()).get("message")

    @staticmethod
    async def test_scenarios_as_dict(aiohttp_client, routes, loop):
        catcher = Catcher()
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

        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/divide?a=10&b=0")
        assert 400 == resp.status
        assert "Zero division makes zero sense" == (await resp.json()).get("message")

        resp = await client.get("/user/1009")
        assert 404 == resp.status
        assert "User ID 1009 could not be found" == (await resp.json()).get("message")

        resp = await client.get("/get-element-n?n=100")
        assert 418 == resp.status
        assert "Out of bound: range object index out of range" == (await resp.json()).get("message")

    @staticmethod
    async def test_return_constant_message(aiohttp_client, routes, loop):
        catcher = Catcher()
        app = web.Application(middlewares=[catcher.middleware])
        app.add_routes(routes)

        client = await aiohttp_client(app)
        resp = await client.get("/concat?a=Foo&b=Bar")
        assert 200 == resp.status
        assert "FooBar" == (await resp.json()).get("result")

        resp = await client.get("/divide?a=Foo")
        assert 500 == resp.status