from rest_framework.response import Response
from rest_framework import status


DEFAULT_ERROR_RESPONSE = 'An unexpected error occurred. Please try again later or contact the administrator.'


def rest_framework_validation_error(e, default_msg):
    '''Response when DRF generates validation error'''
    try:
        err_message = [e.detail[err][0] for err in e.detail][0]
    except:
        err_message = default_msg
    return Response(
        data=err_message,
        status=status.HTTP_400_BAD_REQUEST
    )
