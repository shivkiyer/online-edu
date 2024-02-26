from .error_definitions import DEFAULT_ERROR_RESPONSE


def extract_serializer_error(error, default_msg=DEFAULT_ERROR_RESPONSE):
    '''
    Return error message from serializer error object

    Parameters
    --------------
    error : dict
        Dictionary of serializer errors
    default_msg : str
        Default error message

    Returns
    --------------
    err_message : str
        One of the error messages in serializer
        error dictionary or default error message
    '''
    try:
        err_message = [error[e][0]
                       for e in error][0]
    except:
        err_message = default_msg
    return err_message
