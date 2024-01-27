from django.db import models

from common.error_definitions import Http400Error, Http404Error


class CourseManager(models.Manager):
    '''Manager for Course model'''

    def fetch_courses(self, is_draft=False, is_archived=False):
        return self.get_queryset().filter(is_draft=is_draft, is_archived=is_archived)

    def get_course_by_slug(self, slug):
        '''Return course using slug field'''
        if slug is None:
            raise Http400Error('Slug missing')
        try:
            return self.get_queryset().get(slug=slug)
        except:
            raise Http404Error('Course not found')
