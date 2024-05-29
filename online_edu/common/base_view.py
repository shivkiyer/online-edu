from django.utils import translation
from rest_framework.generics import GenericAPIView


class BaseAPIView(GenericAPIView):
    '''
    Base API view for handling language content
    '''

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        lang = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if lang is not None:
            translation.activate(lang)
