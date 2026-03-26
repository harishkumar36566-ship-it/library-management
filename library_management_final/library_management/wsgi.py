"""
WSGI config for library_management project.

It exposes the WSGI callable as a module-level variable named `application`.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'library_management' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')

# Create the WSGI application object
application = get_wsgi_application()