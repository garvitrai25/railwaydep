import os
import sys
from decimal import Decimal

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
django.setup()

from django.contrib.auth.models import User

from agro.models import Category, ProductItem

# New categories for agricultural equipment
equipment_categories = [
    "Tractors & Power",
    "Harvesting Equipment",
    "Planting Equipment",
    "Irrigation Systems",
    "Storage Equipment",
    "Farm Tools",
    "Pest Control",
    "Livestock Equipment"
]

# Create categories
for category_name in equipment_categories:
    category, created = Category.objects.get_or_create(category_name=category_name)
    print(f"Category {'created' if created else 'already exists'}: {category_name}")

# Get admin user
admin_user = User.objects.get(username='admin')

# Agricultural equipment products
equipment_products = [
    {
        "title": "Mahindra 575 DI XP Plus Tractor",
        "description": "Powerful 47 HP tractor with 4-wheel drive, perfect for heavy-duty farming. Features include power steering, oil immersed brakes, and 12+3 gearbox. Ideal for both wet and dry field operations.",
        "price": Decimal("850000.00"),  # ₹8,50,000
        "quantity": 5,
        "unit": "unit",
        "category": "Tractors & Power",
        "post_type": "FS"
    },
    {
        "title": "John Deere Self-Propelled Harvester",
        "description": "Advanced harvesting machine with 200 HP engine, suitable for wheat, rice, and other grains. Features GPS navigation and yield monitoring system.",
        "price": Decimal("2200000.00"),  # ₹22,00,000
        "quantity": 3,
        "unit": "unit",
        "category": "Harvesting Equipment",
        "post_type": "FS"
    },
    {
        "title": "Automated Seed Drill",
        "description": "Modern 16-row seed drill with precise depth control and seed spacing. Includes digital monitoring system and fertilizer attachment.",
        "price": Decimal("175000.00"),  # ₹1,75,000
        "quantity": 8,
        "unit": "unit",
        "category": "Planting Equipment",
        "post_type": "FS"
    },
    {
        "title": "Drip Irrigation System Kit",
        "description": "Complete drip irrigation system for 1 acre. Includes filters, pressure regulators, drip lines, and digital controller. Water-efficient and easy to install.",
        "price": Decimal("45000.00"),  # ₹45,000
        "quantity": 15,
        "unit": "set",
        "category": "Irrigation Systems",
        "post_type": "FS"
    },
    {
        "title": "Grain Storage Silo",
        "description": "500-ton capacity steel silo with temperature monitoring system. Features aeration system and moisture control. Perfect for long-term grain storage.",
        "price": Decimal("350000.00"),  # ₹3,50,000
        "quantity": 4,
        "unit": "unit",
        "category": "Storage Equipment",
        "post_type": "FS"
    },
    {
        "title": "Premium Farm Tool Set",
        "description": "Comprehensive set of 25 essential farming tools including spades, hoes, pruning shears, and harvesting knives. Made from high-quality stainless steel.",
        "price": Decimal("12000.00"),  # ₹12,000
        "quantity": 20,
        "unit": "set",
        "category": "Farm Tools",
        "post_type": "FS"
    },
    {
        "title": "Automated Pesticide Sprayer",
        "description": "Battery-operated backpack sprayer with 16L capacity. Features adjustable nozzle and pressure control. Includes protective gear kit.",
        "price": Decimal("8500.00"),  # ₹8,500
        "quantity": 25,
        "unit": "unit",
        "category": "Pest Control",
        "post_type": "FS"
    },
    {
        "title": "Dairy Farm Milking Machine",
        "description": "Double bucket milking machine with vacuum pump. Stainless steel construction with easy cleaning system. Suitable for small to medium dairy farms.",
        "price": Decimal("65000.00"),  # ₹65,000
        "quantity": 10,
        "unit": "unit",
        "category": "Livestock Equipment",
        "post_type": "FS"
    },
    {
        "title": "Solar Water Pump System",
        "description": "5 HP solar-powered water pump with controller. Includes solar panels and mounting structure. Ideal for irrigation in remote areas.",
        "price": Decimal("175000.00"),  # ₹1,75,000
        "quantity": 7,
        "unit": "set",
        "category": "Irrigation Systems",
        "post_type": "FS"
    },
    {
        "title": "Mini Rice Harvester",
        "description": "Compact self-propelled rice harvester suitable for small fields. 2-meter cutting width with grain tank. Fuel-efficient design.",
        "price": Decimal("450000.00"),  # ₹4,50,000
        "quantity": 6,
        "unit": "unit",
        "category": "Harvesting Equipment",
        "post_type": "FS"
    },
    {
        "title": "Rotavator",
        "description": "Heavy-duty rotavator with 48 blades. Working width of 1.65m. Perfect for soil preparation and mixing crop residue.",
        "price": Decimal("125000.00"),  # ₹1,25,000
        "quantity": 12,
        "unit": "unit",
        "category": "Tractors & Power",
        "post_type": "FS"
    },
    {
        "title": "Poultry Farm Equipment Set",
        "description": "Complete set including automatic feeders, drinkers, and climate control system. Suitable for 1000-bird capacity farm.",
        "price": Decimal("225000.00"),  # ₹2,25,000
        "quantity": 5,
        "unit": "set",
        "category": "Livestock Equipment",
        "post_type": "FS"
    },
    {
        "title": "Smart Greenhouse Kit",
        "description": "100 sq.m greenhouse with automated climate control. Includes drip irrigation, fans, and monitoring system.",
        "price": Decimal("285000.00"),  # ₹2,85,000
        "quantity": 3,
        "unit": "set",
        "category": "Storage Equipment",
        "post_type": "FS"
    },
    {
        "title": "Electric Chaff Cutter",
        "description": "3 HP motor with safety switch. Suitable for both dry and green fodder. High-quality steel blades.",
        "price": Decimal("35000.00"),  # ₹35,000
        "quantity": 15,
        "unit": "unit",
        "category": "Livestock Equipment",
        "post_type": "FS"
    },
    {
        "title": "Professional Soil Testing Kit",
        "description": "Advanced soil testing equipment with digital pH meter. Tests for N, P, K, and micronutrients. Includes 100 test strips.",
        "price": Decimal("18500.00"),  # ₹18,500
        "quantity": 20,
        "unit": "kit",
        "category": "Farm Tools",
        "post_type": "FS"
    }
]

# Create products
for product_data in equipment_products:
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
            image="productImage/default.jpg"  # Default image
        )
        product.save()
        print(f"Created product: {product_data['title']}")
    else:
        print(f"Product already exists: {product_data['title']}")

print("Agricultural equipment data creation completed!") 