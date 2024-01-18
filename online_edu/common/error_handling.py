import logging
from rest_framework.response import Response
from rest_framework import status

from .error_definitions import DEFAULT_ERROR_RESPONSE, \
    Http400Error

logger = logging.getLogger(__name__)


def rest_framework_validation_error(e, default_msg=DEFAULT_ERROR_RESPONSE):
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


def serializer_error_response(serializer, default_msg=DEFAULT_ERROR_RESPONSE):
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


def extract_serializer_error(error, default_msg=DEFAULT_ERROR_RESPONSE):
    '''Return error string as generic error'''
    try:
        err_message = [error[e][0].title()
                       for e in error][0]
    except:
        err_message = default_msg
    return err_message
