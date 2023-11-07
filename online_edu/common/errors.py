import logging
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

DEFAULT_ERROR_RESPONSE = 'An unexpected error occurred. Please try again later or contact the administrator.'


def rest_framework_validation_error(e, default_msg):
    '''Response 400 when DRF generates validation error'''
    try:
        err_message = [e.detail[err][0] for err in e.detail][0]
    except:
        err_message = default_msg
    logger.error('Error in handling request - {}'.format(err_message))
    return Response(
        data=err_message,
        status=status.HTTP_400_BAD_REQUEST
    )


def serializer_error_response(serializer, default_msg):
    '''Return 400 HTTP error if serializer has errors'''
    try:
        err_message = [serializer.errors[e][0].title()
                       for e in serializer.errors][0]
    except:
        err_message = default_msg
    logger.error('Error in saving data - {}'.format(err_message))
    return Response(
        data=err_message,
        status=status.HTTP_400_BAD_REQUEST
    )
