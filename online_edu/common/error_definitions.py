from rest_framework.exceptions import APIException

DEFAULT_ERROR_RESPONSE = 'An unexpected error occurred. Please try again later or contact the administrator.'


class CustomAPIError(APIException):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
