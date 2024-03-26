import os
from shutil import rmtree

from django.conf import settings


def clean_test_media():
    '''
    Removes the test_media directory after tests
    '''
    # Explicitly specifying test_media and not
    # settings.MEDIA_ROOT to avoid any accidental
    # deletions
    rmtree(
        os.path.join(settings.BASE_DIR, 'test_media'),
        ignore_errors=True
    )
