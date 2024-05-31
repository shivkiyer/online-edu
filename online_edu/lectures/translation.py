from modeltranslation.translator import translator, TranslationOptions

from .models import Lecture


class LectureTranslation(TranslationOptions):
    '''
    Translation of Lecture model
    '''
    fields = ('title', 'description')


translator.register(Lecture, LectureTranslation)
