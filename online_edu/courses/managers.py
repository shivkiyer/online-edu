import logging
from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError

logger = logging.getLogger(__name__)


class CourseManager(models.Manager):
    '''
    Manager for Course model

    Methods
    -------------
    fetch_courses(is_draft=False, is_archived=False):
        Returns list of published courses that are not archived

    get_course_by_slug(slug, admin_only=True):
        Returns course object from course slug
    '''

    def fetch_courses(self, is_draft=False, is_archived=False):
        '''
        Return course list

        Parameters
        ------------
        is_draft : boolean, optional
            Can the courses be in draft mode (not published).
            Default is False.
        is_archived : boolean, optional
            Can the courses be archived. Default is False.

        Returns
        ------------
        Queryset of course model instances.
        '''
        return self.get_queryset().filter(is_draft=is_draft, is_archived=is_archived)

    def get_course_by_slug(self, slug, admin_only=True):
        '''
        Return course using slug field. If admin_only is False, course
        should be published and should not be archived.

        Parameters
        -------------
        slug : str
            Course slug
        admin_only : boolean, optional
            Can only an admin access the course.
            Default is True.

        Raises
        -------------
        400 error
            If parameter slug is missing
        404 error
            If course is not found or if course is
            not published or archived but admin_only
            parameter is False

        Returns
        -------------
        Course model instance
        '''
        if slug is None:
            logger.error('Course fetched without slug')
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Slug missing'
            )
        try:
            course = self.get_queryset().get(slug=slug)
            if not admin_only:
                if course.is_draft or course.is_archived:
                    logger.critical(
                        'Non-admin user viewing unpublished or archived course'
                    )
                    raise
            return course
        except:
            logger.error(f'Course with slug {slug} not found')
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Course not found'
            )
