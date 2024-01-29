from django.db import models

from common.error_definitions import Http400Error


class LectureManager(models.Manager):
    '''Manager for Lecture model'''

    def check_title_duplicate(self, course, title):
        '''Check if course with same title exists in course'''
        if course is None:
            raise Http400Error('Course must be specified to verify title')
        if title is None:
            raise Http400Error('Title is required')
        try:
            course_obj = self.get_queryset().get(
                course=course,
                title=title
            )
        except:
            return False
        raise Http400Error('Lecture with the same title exists in the course')
