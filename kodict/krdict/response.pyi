from typing import Any
from aiohttp import Response

from .types import ViewResponse
from .main import ErrorResponse, TSearchResponse

def parse_response(
    kwargs: dict[str, Any],
    api_response: Response,
    request_params: dict[str, Any],
    search_type: str
) -> TSearchResponse | ErrorResponse | ViewResponse: ...
