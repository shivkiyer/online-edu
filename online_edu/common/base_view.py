from django.utils import translation
from django.conf import settings
from rest_framework.generics import GenericAPIView


class BaseAPIView(GenericAPIView):
    '''
    Base API view for handling language content
    '''

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        check_language = translation.get_language()
        # LocaleMiddleware has already set language
        if not check_language == settings.LANGUAGE_CODE:
            return
        lang = request.META.get('HTTP_ACCEPT_LANGUAGE')
        supported_languages = dict(settings.LANGUAGES)
        if lang is not None:
            if '_' in lang:
                lang = lang.split('_')[0]
            if lang in supported_languages:
                translation.activate(lang)
