import logging
import os
import sys

from django.core.wsgi import get_wsgi_application

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    # Initialize Django WSGI application
    logging.info("Initializing Django WSGI application...")
    application = get_wsgi_application()
    app = application
    logging.info("Django WSGI application initialized successfully")
except Exception as e:
    logging.error(f"Error loading WSGI application: {str(e)}")
    logging.error("Python path: " + str(sys.path))
    logging.error("Current directory: " + os.getcwd())
    raise e

# Init Vercel serverless function
application = app 
