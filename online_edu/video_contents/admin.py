from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import VideoContent


class VideoContentAdmin(TranslationAdmin):
    '''
    Translation of VideoContent model for admin
    '''


admin.site.register(VideoContent, VideoContentAdmin)
