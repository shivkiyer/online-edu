from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Course


class CourseAdmin(TranslationAdmin):
    '''
    Translated model of Course model for admin
    '''
    pass


admin.site.register(Course, CourseAdmin)
