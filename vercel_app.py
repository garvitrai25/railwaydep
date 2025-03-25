import os

from django.core.wsgi import get_wsgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    # Initialize Django WSGI application
    application = get_wsgi_application()
    # Alias the application for Vercel
    app = application
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise e

# Init Vercel serverless function
application = app 
