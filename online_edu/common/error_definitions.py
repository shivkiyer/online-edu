DEFAULT_ERROR_RESPONSE = 'An unexpected error occurred. Please try again later or contact the administrator.'


class Http400Error(Exception):
    '''Raised for 400 (bad data) error responses'''
    pass


class Http401Error(Exception):
    '''Raised for 401 (unauthorized) error responses'''
    pass


class Http403Error(Exception):
    '''Raised for 403 (forbidden) error responses'''
    pass


class Http404Error(Exception):
    '''Raised for 404 (not found) error response'''
    pass
