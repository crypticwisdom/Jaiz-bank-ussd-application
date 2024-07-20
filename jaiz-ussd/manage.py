import os
import sys
from decouple import config

f = open('.env', 'a+')
f.close()

def main():
    """Run administrative tasks."""
    if config('env', '') == 'prod':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaizussd.settings.prod')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaizussd.settings.dev')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
