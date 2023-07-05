from typing import Any, Literal, Tuple
from aiohttp import Response
from .main import TSearchType

def send_request(
    kwargs: dict[str, Any], 
    advanced: bool = False, 
    search_type: TSearchType | Literal['view'] | None = None
) -> Tuple[Response, dict[str, Any], str]: ...

def set_key(key: str | None) -> None: ...

def transform_search_params(params: dict[str, Any]) -> None: ...

def transform_view_params(params: dict[str, Any]) -> None: ...
