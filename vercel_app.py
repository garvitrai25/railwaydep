import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

from wsgi import app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django WSGI application
application = get_wsgi_application()

# Init Vercel serverless function
application = app 
