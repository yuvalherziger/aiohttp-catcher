from typing import Optional

from aiohttp.web import Request
from aiohttp.web_exceptions import (
    HTTPError, HTTPBadRequest, HTTPUnauthorized, HTTPPaymentRequired, HTTPForbidden, HTTPNotFound,
    HTTPMethodNotAllowed, HTTPNotAcceptable, HTTPProxyAuthenticationRequired, HTTPRequestTimeout, HTTPConflict,
    HTTPGone, HTTPLengthRequired, HTTPPreconditionFailed, HTTPRequestEntityTooLarge, HTTPRequestURITooLong,
    HTTPUnsupportedMediaType, HTTPRequestRangeNotSatisfiable, HTTPExpectationFailed, HTTPMisdirectedRequest,
    HTTPUnprocessableEntity, HTTPFailedDependency, HTTPUpgradeRequired, HTTPPreconditionRequired,
    HTTPTooManyRequests, HTTPRequestHeaderFieldsTooLarge, HTTPUnavailableForLegalReasons, HTTPInternalServerError,
    HTTPNotImplemented, HTTPBadGateway, HTTPServiceUnavailable, HTTPGatewayTimeout, HTTPVersionNotSupported,
    HTTPVariantAlsoNegotiates, HTTPInsufficientStorage, HTTPNotExtended, HTTPNetworkAuthenticationRequired,
)

from aiohttp_catcher import catch


async def get_aiohttp_error_message(exc: HTTPError,
                                    request: Optional[Request] = None) -> str:  # pylint: disable=unused-argument
    return exc.__class__.__name__


SCENARIOS = [
    catch(HTTPBadRequest).with_status_code(400).and_call(get_aiohttp_error_message),
    catch(HTTPUnauthorized).with_status_code(401).and_call(get_aiohttp_error_message),
    catch(HTTPPaymentRequired).with_status_code(402).and_call(get_aiohttp_error_message),
    catch(HTTPForbidden).with_status_code(403).and_call(get_aiohttp_error_message),
    catch(HTTPNotFound).with_status_code(404).and_call(get_aiohttp_error_message),
    catch(HTTPMethodNotAllowed).with_status_code(405).and_call(get_aiohttp_error_message),
    catch(HTTPNotAcceptable).with_status_code(406).and_call(get_aiohttp_error_message),
    catch(HTTPProxyAuthenticationRequired).with_status_code(407).and_call(get_aiohttp_error_message),
    catch(HTTPRequestTimeout).with_status_code(408).and_call(get_aiohttp_error_message),
    catch(HTTPConflict).with_status_code(409).and_call(get_aiohttp_error_message),
    catch(HTTPGone).with_status_code(410).and_call(get_aiohttp_error_message),
    catch(HTTPLengthRequired).with_status_code(411).and_call(get_aiohttp_error_message),
    catch(HTTPPreconditionFailed).with_status_code(412).and_call(get_aiohttp_error_message),
    catch(HTTPRequestEntityTooLarge).with_status_code(413).and_call(get_aiohttp_error_message),
    catch(HTTPRequestURITooLong).with_status_code(414).and_call(get_aiohttp_error_message),
    catch(HTTPUnsupportedMediaType).with_status_code(415).and_call(get_aiohttp_error_message),
    catch(HTTPRequestRangeNotSatisfiable).with_status_code(416).and_call(get_aiohttp_error_message),
    catch(HTTPExpectationFailed).with_status_code(417).and_call(get_aiohttp_error_message),
    catch(HTTPMisdirectedRequest).with_status_code(421).and_call(get_aiohttp_error_message),
    catch(HTTPUnprocessableEntity).with_status_code(422).and_call(get_aiohttp_error_message),
    catch(HTTPFailedDependency).with_status_code(424).and_call(get_aiohttp_error_message),
    catch(HTTPUpgradeRequired).with_status_code(426).and_call(get_aiohttp_error_message),
    catch(HTTPPreconditionRequired).with_status_code(428).and_call(get_aiohttp_error_message),
    catch(HTTPTooManyRequests).with_status_code(429).and_call(get_aiohttp_error_message),
    catch(HTTPRequestHeaderFieldsTooLarge).with_status_code(431).and_call(get_aiohttp_error_message),
    catch(HTTPUnavailableForLegalReasons).with_status_code(451).and_call(get_aiohttp_error_message),
    catch(HTTPInternalServerError).with_status_code(500).and_call(get_aiohttp_error_message),
    catch(HTTPNotImplemented).with_status_code(501).and_call(get_aiohttp_error_message),
    catch(HTTPBadGateway).with_status_code(502).and_call(get_aiohttp_error_message),
    catch(HTTPServiceUnavailable).with_status_code(503).and_call(get_aiohttp_error_message),
    catch(HTTPGatewayTimeout).with_status_code(504).and_call(get_aiohttp_error_message),
    catch(HTTPVersionNotSupported).with_status_code(505).and_call(get_aiohttp_error_message),
    catch(HTTPVariantAlsoNegotiates).with_status_code(506).and_call(get_aiohttp_error_message),
    catch(HTTPInsufficientStorage).with_status_code(507).and_call(get_aiohttp_error_message),
    catch(HTTPNotExtended).with_status_code(510).and_call(get_aiohttp_error_message),
    catch(HTTPNetworkAuthenticationRequired).with_status_code(511).and_call(get_aiohttp_error_message),
]
