from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Lecture


class LectureAdmin(TranslationAdmin):
    '''
    Translation of Lecture model for admin
    '''
    pass


admin.site.register(Lecture, LectureAdmin)
