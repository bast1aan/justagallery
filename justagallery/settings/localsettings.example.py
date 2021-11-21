import os

from .defaultsettings import *

# SECURITY WARNING: regenerate this key when using in prodution.
SECRET_KEY = 'django-insecure-1234567890abcdef'

DEBUG=False

ALLOWED_HOSTS.append('gallery.example.com')

MEDIA_ROOT = Path('/mnt/storage/justagallery-uploads')

THUMBNAILS_ROOT = Path(os.environ['HOME']) / Path('.cache/justagallery-thumbnails')
if not os.path.exists(THUMBNAILS_ROOT):
	os.makedirs(THUMBNAILS_ROOT)

DATABASES['default'] = {
	'ENGINE': 'django.db.backends.postgresql',
	'NAME': 'justagallery',
	'USER': 'justagallery',
	'PASSWORD': 'v3r4s3cr3t',
	'HOST': '127.0.0.1',
	'PORT': '5432',
}
