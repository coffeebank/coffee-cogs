"""
Contains exception classes.
"""

class KRDictException(Exception):
    """
    Contains information about an API error.
    This exception is only thrown if the argument passed to the
    ``raise_api_errors`` parameter is True.

    - ``message``: The error message associated with the error.
    - ``error_code``: The error code returned by the API.
    - ``request_params``: A dict containing the transformed parameters
    that were sent to the API.
    """

    def __init__(self, message, error_code, request_params):
        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.request_params = request_params

    def __reduce__(self):
        return (KRDictException, (self.message, self.error_code, self.request_params))
