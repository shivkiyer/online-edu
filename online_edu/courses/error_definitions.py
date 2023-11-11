class CourseGenericError(Exception):
    '''Raised for course exceptions'''
    pass


class CourseForbiddenError(Exception):
    '''Raised when a course action is not allowed'''
    pass
