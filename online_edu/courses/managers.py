from django.db import models


class CourseManager(models.Manager):
    '''Manager for Course model'''

    def fetch_courses(self, is_draft=False, is_archived=False):
        return self.get_queryset().filter(is_draft=is_draft, is_archived=is_archived)
