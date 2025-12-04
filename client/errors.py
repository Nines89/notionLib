class NotionError(Exception):
    pass


class InvalidJsonError(NotionError): pass
class InvalidRequestUrl(NotionError): pass
class InvalidRequest(NotionError): pass
class InvalidGrant(NotionError): pass
class ValidationError(NotionError): pass
class MissingVersion(NotionError): pass
class Unauthorized(NotionError): pass
class RestrictedResource(NotionError): pass
class ObjectNotFound(NotionError): pass
class ConflictError(NotionError): pass
class RateLimited(NotionError): pass
class InternalServerError(NotionError): pass
class BadGateway(NotionError): pass
class ServiceUnavailable(NotionError): pass
class DatabaseConnectionUnavailable(NotionError): pass
class GatewayTimeout(NotionError): pass


ERROR_MAP = {
    "invalid_json": InvalidJsonError,
    "invalid_request_url": InvalidRequestUrl,
    "invalid_request": InvalidRequest,
    "invalid_grant": InvalidGrant,
    "validation_error": ValidationError,
    "missing_version": MissingVersion,
    "unauthorized": Unauthorized,
    "restricted_resource": RestrictedResource,
    "object_not_found": ObjectNotFound,
    "conflict_error": ConflictError,
    "rate_limited": RateLimited,
    "internal_server_error": InternalServerError,
    "bad_gateway": BadGateway,
    "service_unavailable": ServiceUnavailable,
    "database_connection_unavailable": DatabaseConnectionUnavailable,
    "gateway_timeout": GatewayTimeout,
}
