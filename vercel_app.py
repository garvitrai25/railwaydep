import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django WSGI application
app = application = get_wsgi_application()

# Init Vercel serverless function
application = app 
