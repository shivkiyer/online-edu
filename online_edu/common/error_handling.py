import logging
from rest_framework.response import Response
from rest_framework import status

from .error_definitions import DEFAULT_ERROR_RESPONSE, \
    Http400Error

logger = logging.getLogger(__name__)


def extract_serializer_error(error, default_msg=DEFAULT_ERROR_RESPONSE):
    '''Return error string as generic error'''
    try:
        err_message = [error[e][0]
                       for e in error][0]
    except:
        err_message = default_msg
    return err_message
