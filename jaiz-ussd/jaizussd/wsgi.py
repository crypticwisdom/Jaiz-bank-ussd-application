import os
from decouple import config

from django.core.wsgi import get_wsgi_application

if config('env', '') == 'prod':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaizussd.settings.prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaizussd.settings.dev')

application = get_wsgi_application()
