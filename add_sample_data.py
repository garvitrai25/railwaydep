import os
import random
import sys
from decimal import Decimal

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Initialize Django
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from django.core.files.images import ImageFile

from account.models import User_info
from agro.models import Category, ProductItem

print("Django setup complete. Starting data creation...")

# Create categories if they don't exist
categories = [
    "Vegetables",
    "Fruits",
    "Grains",
    "Dairy",
    "Meat",
    "Poultry",
    "Seafood",
    "Herbs & Spices",
    "Nuts & Seeds",
    "Organic Products"
]

# Create categories
created_categories = []
for category_name in categories:
    category, created = Category.objects.get_or_create(category_name=category_name)
    created_categories.append(category)
    print(f"Category {'created' if created else 'already exists'}: {category_name}")

# Check if we have a superuser
try:
    admin_user = User.objects.get(username='admin')
    print("Using existing admin user")
except User.DoesNotExist:
    # Create a superuser if it doesn't exist
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword',
        first_name='Admin',
        last_name='User'
    )
    print("Created admin user")

# Create user_info for admin if it doesn't exist
try:
    user_info = User_info.objects.get(user=admin_user)
    print("Admin user_info already exists")
except User_info.DoesNotExist:
    # Create a placeholder image path
    user_info = User_info.objects.create(
        user=admin_user,
        gender='M',
        address='123 Admin Street',
        phone='1234567890',
        user_type='S',
        profile_pic='profilepic/default.jpg'  # This will need to be a valid image path
    )
    print("Created admin user_info")

# Sample products data
products_for_sale = [
    {
        "title": "Fresh Organic Tomatoes",
        "description": "Vine-ripened organic tomatoes, perfect for salads and cooking. Grown without pesticides or chemical fertilizers.",
        "price": Decimal("2.99"),
        "quantity": 50,
        "unit": "kg",
        "category": "Vegetables",
        "post_type": "FS"  # For Sale
    },
    {
        "title": "Premium Basmati Rice",
        "description": "Long-grain aromatic rice, aged for 2 years for the perfect texture and flavor. Ideal for biryanis and pilafs.",
        "price": Decimal("5.49"),
        "quantity": 100,
        "unit": "kg",
        "category": "Grains",
        "post_type": "FS"
    },
    {
        "title": "Organic Honey",
        "description": "Pure, raw, and unfiltered honey from wildflower meadows. Collected from bees that pollinate organic farms only.",
        "price": Decimal("8.99"),
        "quantity": 30,
        "unit": "liter",
        "category": "Organic Products",
        "post_type": "FS"
    },
    {
        "title": "Fresh Farm Eggs",
        "description": "Free-range eggs from hens raised on organic feed. Rich in nutrients with bright orange yolks.",
        "price": Decimal("3.99"),
        "quantity": 200,
        "unit": "dozen",
        "category": "Poultry",
        "post_type": "FS"
    },
    {
        "title": "Organic Apples",
        "description": "Crisp and sweet apples grown using organic farming methods. Perfect for snacking or baking.",
        "price": Decimal("1.99"),
        "quantity": 150,
        "unit": "kg",
        "category": "Fruits",
        "post_type": "FS"
    },
    {
        "title": "Fresh Carrots",
        "description": "Sweet and crunchy carrots, freshly harvested from our organic farm. Rich in beta-carotene and antioxidants.",
        "price": Decimal("1.49"),
        "quantity": 100,
        "unit": "kg",
        "category": "Vegetables",
        "post_type": "FS"
    },
    {
        "title": "Organic Strawberries",
        "description": "Juicy, sweet strawberries grown without pesticides. Perfect for desserts or eating fresh.",
        "price": Decimal("4.99"),
        "quantity": 50,
        "unit": "kg",
        "category": "Fruits",
        "post_type": "FS"
    },
    {
        "title": "Free-Range Chicken",
        "description": "Humanely raised, free-range chicken fed with organic grains. No antibiotics or hormones.",
        "price": Decimal("7.99"),
        "quantity": 30,
        "unit": "kg",
        "category": "Poultry",
        "post_type": "FS"
    },
    {
        "title": "Organic Quinoa",
        "description": "High-protein, gluten-free quinoa grown using sustainable farming practices. Perfect for salads and side dishes.",
        "price": Decimal("6.49"),
        "quantity": 80,
        "unit": "kg",
        "category": "Grains",
        "post_type": "FS"
    },
    {
        "title": "Fresh Basil",
        "description": "Aromatic basil leaves, perfect for Italian cuisine. Grown in our greenhouse without pesticides.",
        "price": Decimal("2.49"),
        "quantity": 20,
        "unit": "kg",
        "category": "Herbs & Spices",
        "post_type": "FS"
    }
]

products_for_buy = [
    {
        "title": "Bulk Wheat Grain",
        "description": "Looking to purchase high-quality wheat grain in bulk for flour production. Must be pesticide-free and recently harvested.",
        "price": Decimal("1.50"),
        "quantity": 1000,
        "unit": "kg",
        "category": "Grains",
        "post_type": "FB"  # For Buy
    },
    {
        "title": "Organic Milk",
        "description": "Seeking regular supply of organic, grass-fed cow's milk for artisanal cheese production. Must be hormone-free.",
        "price": Decimal("0.95"),
        "quantity": 500,
        "unit": "liter",
        "category": "Dairy",
        "post_type": "FB"
    },
    {
        "title": "Fresh Herbs Assortment",
        "description": "Looking for a variety of fresh culinary herbs including basil, thyme, rosemary, and mint for restaurant use.",
        "price": Decimal("4.25"),
        "quantity": 20,
        "unit": "kg",
        "category": "Herbs & Spices",
        "post_type": "FB"
    },
    {
        "title": "Organic Potatoes",
        "description": "Seeking regular supply of organic potatoes for farm-to-table restaurant. Multiple varieties preferred.",
        "price": Decimal("1.25"),
        "quantity": 200,
        "unit": "kg",
        "category": "Vegetables",
        "post_type": "FB"
    },
    {
        "title": "Raw Almonds",
        "description": "Looking to purchase raw, unprocessed almonds in bulk for health food production. Must be certified organic.",
        "price": Decimal("9.99"),
        "quantity": 50,
        "unit": "kg",
        "category": "Nuts & Seeds",
        "post_type": "FB"
    },
    {
        "title": "Fresh Salmon",
        "description": "Seeking wild-caught salmon for high-end restaurant. Must be sustainably sourced and delivered fresh.",
        "price": Decimal("15.99"),
        "quantity": 30,
        "unit": "kg",
        "category": "Seafood",
        "post_type": "FB"
    },
    {
        "title": "Organic Beef",
        "description": "Looking for grass-fed, organic beef for premium burger restaurant. Need regular supply.",
        "price": Decimal("12.50"),
        "quantity": 100,
        "unit": "kg",
        "category": "Meat",
        "post_type": "FB"
    },
    {
        "title": "Seasonal Berries",
        "description": "Seeking various seasonal berries (blueberries, raspberries, blackberries) for artisanal jam production.",
        "price": Decimal("8.75"),
        "quantity": 75,
        "unit": "kg",
        "category": "Fruits",
        "post_type": "FB"
    },
    {
        "title": "Organic Flour",
        "description": "Looking for high-quality organic flour for artisanal bakery. Need consistent texture and protein content.",
        "price": Decimal("2.25"),
        "quantity": 300,
        "unit": "kg",
        "category": "Grains",
        "post_type": "FB"
    },
    {
        "title": "Fresh Garlic",
        "description": "Seeking regular supply of fresh garlic bulbs for restaurant use. Prefer locally grown.",
        "price": Decimal("3.50"),
        "quantity": 25,
        "unit": "kg",
        "category": "Herbs & Spices",
        "post_type": "FB"
    }
]

# Create products
for product_data in products_for_sale + products_for_buy:
    # Get the category
    category = Category.objects.get(category_name=product_data["category"])
    
    # Check if product already exists
    if not ProductItem.objects.filter(title=product_data["title"]).exists():
        # Create the product
        product = ProductItem(
            user=admin_user,
            title=product_data["title"],
            description=product_data["description"],
            price=product_data["price"],
            quantity=product_data["quantity"],
            unit=product_data["unit"],
            category=category,
            post_type=product_data["post_type"],
            status=True,
            # We'll need to handle the image separately
            image="productImage/default.jpg"  # This will need to be a valid image path
        )
        product.save()
        print(f"Created product: {product_data['title']}")
    else:
        print(f"Product already exists: {product_data['title']}")

print("Sample data creation completed!") 