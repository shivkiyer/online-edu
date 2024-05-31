from modeltranslation.translator import translator, TranslationOptions

from .models import VideoContent


class VideoContentTranslation(TranslationOptions):
    '''
    Translation of VideoContent model
    '''
    fields = ('name',)


translator.register(VideoContent, VideoContentTranslation)
