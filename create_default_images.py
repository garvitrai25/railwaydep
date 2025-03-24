import os
import random

from PIL import Image, ImageDraw, ImageFont

# Create directories if they don't exist
os.makedirs('media/productImage', exist_ok=True)
os.makedirs('media/profilepic', exist_ok=True)

# Create a default product image
def create_product_image():
    # Create a 500x500 image with a random background color
    img = Image.new('RGB', (500, 500), color=(
        random.randint(200, 255),
        random.randint(200, 255),
        random.randint(200, 255)
    ))
    
    # Draw on the image
    draw = ImageDraw.Draw(img)
    
    # Draw a border
    draw.rectangle([(10, 10), (490, 490)], outline=(100, 100, 100), width=2)
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("Arial", 40)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    draw.text((150, 200), "Product", fill=(0, 0, 0), font=font)
    draw.text((150, 250), "Image", fill=(0, 0, 0), font=font)
    
    # Save the image
    img.save('media/productImage/default.jpg')
    print("Created default product image at media/productImage/default.jpg")

# Create a default profile image
def create_profile_image():
    # Create a 300x300 image with a light blue background
    img = Image.new('RGB', (300, 300), color=(200, 220, 255))
    
    # Draw on the image
    draw = ImageDraw.Draw(img)
    
    # Draw a circle for the head
    draw.ellipse([(75, 75), (225, 225)], fill=(240, 240, 240))
    
    # Draw a body
    draw.rectangle([(125, 225), (175, 275)], fill=(240, 240, 240))
    
    # Save the image
    img.save('media/profilepic/default.jpg')
    print("Created default profile image at media/profilepic/default.jpg")

if __name__ == "__main__":
    create_product_image()
    create_profile_image()
    print("Default images created successfully!") 