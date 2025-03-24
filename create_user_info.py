import os
import sys

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Initialize Django
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User

from account.models import User_info

# Get username from command line argument or use default
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = input("Enter your username: ")

try:
    # Get the user
    user = User.objects.get(username=username)
    print(f"Found user: {user.username}")
    
    # Check if User_info already exists
    try:
        user_info = User_info.objects.get(user=user)
        print(f"User_info already exists for {user.username}")
    except User_info.DoesNotExist:
        # Create User_info
        user_info = User_info(
            user=user,
            gender='M',  # Default value, can be changed later
            address='Your Address',  # Default value
            phone='Your Phone Number',  # Default value
            user_type='B',  # Default as Buyer, can be changed later
            profile_pic='profilepic/default.jpg'  # Using default profile pic
        )
        user_info.save()
        print(f"Created User_info for {user.username}")
        
except User.DoesNotExist:
    print(f"User with username '{username}' does not exist")
    print("Available users:")
    for user in User.objects.all():
        print(f"- {user.username}") 