import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application

# Initialize Django WSGI application
app = get_wsgi_application()

# Init Vercel serverless function
application = app 
