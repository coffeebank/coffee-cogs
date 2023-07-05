class KRDictException(Exception):
    message: str
    error_code: int
    request_params: dict
