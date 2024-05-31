from modeltranslation.translator import translator, TranslationOptions

from .models import Course


class CourseTranslation(TranslationOptions):
    '''
    Translation of Course model
    '''
    fields = ('title', 'subtitle', 'description')


translator.register(Course, CourseTranslation)
