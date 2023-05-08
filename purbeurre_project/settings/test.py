from . import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'circle_test',
        'USER': 'circleci',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}
