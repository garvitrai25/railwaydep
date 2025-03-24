import time
import uuid
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection, transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CartForm, ComplainForm, OrderForm, ProductForm
from .models import (BeatItem, Cart, Category, Complain, ContactUs,
                     EmailSubscription, Notification, Order, OrderItem,
                     ProductItem, Review)


def pagination(products, page):
    products_paginator = Paginator(products, 10)
    try:
        products = products_paginator.page(page)
    except PageNotAnInteger:
        products = products_paginator.page(1)
    except EmptyPage:
        products = products_paginator.page(products_paginator.num_pages)
    return products


def product_search(search, category, post_type):

    if search:
        products = ProductItem.objects.filter(title__icontains=search,
                                              status=True, post_type=post_type)
    elif category:
        products = ProductItem.objects.filter(category=category,
                                              status=True, post_type=post_type)
    else:
        products = ProductItem.objects.filter(status=True, post_type=post_type)

    return products


def home(request):
    context = {}
    # Get featured products for the homepage
    sale_products = ProductItem.objects.filter(status=True, post_type="FS").order_by('-create_date')[:4]
    buy_products = ProductItem.objects.filter(status=True, post_type="FB").order_by('-create_date')[:4]
    
    context['sale_products'] = sale_products
    context['buy_products'] = buy_products
    
    return render(request, 'index.html', context)


def sale_page(request):
    context = {}
    if request.user.is_authenticated:
        products = ProductItem.objects.filter(user=request.user, post_type="FS").order_by('-id')
        context['products'] = products
    return render(request, 'sell.html', context)


def buy_page(request):
    context = {}
    search = request.GET.get('search')
    category = request.GET.get('category')
    page = request.GET.get('page', 1)

    products = product_search(search, category, "FS").order_by('-id')

    context['categories'] = Category.objects.all()
    context['products'] = pagination(products, page)
    return render(request, 'shop.html', context)


@login_required
def detail(request, id):
    product = get_object_or_404(ProductItem, pk=id)
    cart_items = Cart.objects.filter(user=request.user.id).filter(product=id)

    # Get reviews for this product
    reviews = Review.objects.filter(product=product)
    user_has_reviewed = reviews.filter(user=request.user).exists() if request.user.is_authenticated else False
    
    # Check if user has purchased this product
    can_review = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            user=request.user, 
            status='COMPLETED', 
            orderitem__product=product
        ).exists()
        can_review = has_purchased and not user_has_reviewed

    # Get related products
    related_products = ProductItem.objects.filter(
        category=product.category
    ).exclude(pk=id).order_by('-create_date')[:4]

    context = {
        'product': product,
        'cart_items': cart_items,
        'related_products': related_products,
        'reviews': reviews,
        'can_review': can_review,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'detail.html', context)


def add_product(request):
    context = {}
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('userprofile')
    context['form'] = ProductForm()
    return render(request, 'add-product.html', context)


def add_complain(request):
    context = {}
    if request.method == 'POST':
        form = ComplainForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('userprofile')
    context['form'] = ComplainForm()
    return render(request, 'complain.html', context)


def edit_product(request, id):
    context = {}
    data = ProductItem.objects.get(id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('userprofile')
    context['form'] = ProductForm(instance=data)
    return render(request, 'edit-product.html', context)


def delete_product(request, id):
    ProductItem.objects.get(id=id).delete()
    return redirect('userprofile')


def reply(request):
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        reply = request.POST.get('reply')
        product = get_object_or_404(ProductItem, pk=product_id)
        BeatItem.objects.create(user=user, product=product, reply=reply)
    return redirect(request.META['HTTP_REFERER'])


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and subject and message:
            try:
                # Save the contact message to database
                contact_obj = ContactUs(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                contact_obj.save()
                
                # Check if we're using the console backend
                using_console_backend = 'console' in settings.EMAIL_BACKEND
                
                # Set a flag to track if email was sent successfully
                email_sent = False
                
                try:
                    formatted_message = f"""
From: {name} <{email}>
Subject: {subject}

Message:
{message}

---
This message was sent from the contact form on your website.
"""
                    recipient_email = settings.EMAIL_HOST_USER
                    
                    print(f"Sending email to: {recipient_email}")
                    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
                    print(f"Subject: Contact Form: {subject}")
                    
                    # Attempt to send the email
                    send_mail(
                        f"Contact Form: {subject}", 
                        formatted_message, 
                        settings.DEFAULT_FROM_EMAIL, 
                        [recipient_email],
                        fail_silently=False,
                    )
                    
                    # If we get here, the email was sent successfully
                    email_sent = True
                    
                    # Show success message
                    messages.success(
                        request, f"✅ MESSAGE SENT SUCCESSFULLY! Hello {name}, thanks for contacting us! We'll get back to you soon.")
                    print(f"Email sent successfully to {recipient_email}")
                    
                except Exception as e:
                    # If using console backend, still show success message
                    if using_console_backend:
                        messages.success(
                            request, f"✅ MESSAGE SENT SUCCESSFULLY! Hello {name}, thanks for contacting us! We'll get back to you soon.")
                        print(f"Email content printed to console (using console backend)")
                        email_sent = True
                    else:
                        messages.error(request, f"❌ MESSAGE NOT SENT! An error occurred while sending your message. Your message has been saved in our database, but the email notification failed.")
                        print(f"Email error: {str(e)}")
                    
                    # Print fallback information for debugging
                    print("\n--- EMAIL CONTENT (FALLBACK) ---")
                    print(f"To: {settings.EMAIL_HOST_USER}")
                    print(f"From: {name} <{email}>")
                    print(f"Subject: {subject}")
                    print(f"Message: {message}")
                    print("--- END EMAIL CONTENT ---\n")
                
                # Return a JSON response if this is an AJAX request
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': email_sent,
                        'message': 'Message sent successfully!' if email_sent else 'Message saved but email notification failed.'
                    })
            except Exception as ex:
                print(f"Error saving contact message: {str(ex)}")
                messages.error(request, f"❌ MESSAGE NOT SENT! An error occurred: {str(ex)}")
                
        else:
            messages.error(request, "❌ MESSAGE NOT SENT! Please fill in all fields.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))


def email_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            EmailSubscription(email=email).save()
    return redirect(request.META['HTTP_REFERER'])


# Cart Views
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(ProductItem, id=product_id)
    
    # Check if product has available quantity
    if product.quantity <= product.sold_quantity:
        messages.error(request, f"Sorry, {product.title} is out of stock!")
        return redirect('detail', id=product_id)
    
    # Check if adding one more would exceed available quantity
    cart_item = Cart.objects.filter(user=request.user, product=product).first()
    current_cart_quantity = cart_item.quantity if cart_item else 0
    
    if current_cart_quantity + 1 > (product.quantity - product.sold_quantity):
        messages.error(request, f"Sorry, only {product.quantity - product.sold_quantity} unit(s) available!")
        return redirect('detail', id=product_id)
    
    # Check if product is already in cart
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(user=request.user, product=product, quantity=1)
    
    messages.success(request, f"{product.title} added to your cart!")
    
    # Create notification
    Notification.objects.create(
        user=request.user,
        title="Product Added to Cart",
        message=f"You've added {product.title} to your cart."
    )
    
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'cart.html', context)


@login_required
def update_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    
    if request.method == 'POST':
        form = CartForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Cart updated successfully!")
    
    return redirect('view_cart')


@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    product_title = cart_item.product.title
    cart_item.delete()
    
    messages.success(request, f"{product_title} removed from your cart!")
    return redirect('view_cart')


# Checkout and Order Views
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('view_cart')
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_total = total
            
            # Ensure both pincode and zipcode fields are set
            pincode_value = form.cleaned_data.get('pincode')
            if pincode_value:
                order.pincode = pincode_value
                order.zipcode = pincode_value
                
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    total=cart_item.product.price * cart_item.quantity
                )
            
            # Clear the cart
            cart_items.delete()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title="Order Placed Successfully",
                message=f"Your order #{order.id} has been placed successfully. Please complete the payment."
            )
            
            # Send email notification
            try:
                subject = f"Order Confirmation - Order #{order.id}"
                message = f"""
                Dear {order.full_name},
                
                Thank you for your order! Your order #{order.id} has been received and is awaiting payment.
                
                Order Total: ${order.order_total}
                Payment Method: {order.get_payment_method_display()}
                
                Please complete your payment to process your order.
                
                Best regards,
                The OAMS Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {str(e)}")
            
            # Redirect to payment page instead of order success
            return redirect('payment', order_id=order.id)
    else:
        # Pre-fill form with user information
        initial_data = {}
        if hasattr(request.user, 'email'):
            initial_data['email'] = request.user.email
        if hasattr(request.user, 'first_name') and hasattr(request.user, 'last_name'):
            initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}"
        
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'checkout.html', context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'order_success.html', context)


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-create_date')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'my_orders.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'order_detail.html', context)


# Notification View
@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'userprofile'))


@login_required
def payment(request, order_id):
    """
    Display the mock payment page for an order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # If payment is already completed, redirect to order detail
    if order.payment_status == 'COMPLETED':
        messages.info(request, "This order has already been paid.")
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order
    }
    
    return render(request, 'mock_payment.html', context)


@login_required
def process_payment(request, order_id):
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found!")
        return redirect('my_orders')
    
    # Check if payment is already completed
    if order.payment_status == 'COMPLETED':
        messages.warning(request, "This order has already been paid for.")
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'credit_card')
        payment_result = request.POST.get('payment_result', 'success')
        
        # Use credit card payment prefix
        payment_prefix = 'CC'
        
        # Format: METHOD-TIMESTAMP-USERID-RANDOMHEX
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        transaction_id = f"{payment_prefix}-{timestamp}-{request.user.id}-{uuid.uuid4().hex[:8]}"
        
        # Add a slight delay to simulate payment processing
        time.sleep(2)
        
        if payment_result == 'success':
            # Check product availability before completing the order
            order_items = OrderItem.objects.filter(order=order)
            unavailable_items = []
            
            for item in order_items:
                product = item.product
                if not product.is_available or (product.available_quantity is not None and product.available_quantity < item.quantity):
                    unavailable_items.append(product.title)
            
            if unavailable_items:
                error_message = f"The following products are no longer available in the requested quantity: {', '.join(unavailable_items)}."
                messages.error(request, error_message)
                return redirect('payment', order_id=order_id)
            
            # Update order status to completed
            order.status = 'COMPLETED'
            order.payment_status = 'COMPLETED'
            order.transaction_id = transaction_id
            order.save()
            
            # Update product quantities
            for item in order_items:
                product = item.product
                
                # Ensure sold_quantity is initialized
                if not hasattr(product, 'sold_quantity') or product.sold_quantity is None:
                    product.sold_quantity = 0
                    
                # Update sold quantity regardless of who is buying
                product.sold_quantity += item.quantity
                product.save()
                
                # Debug log for quantity update
                print(f"Updated product {product.id} ({product.title}): sold_quantity now {product.sold_quantity}, total quantity: {product.quantity}")
                
                # Create notification for seller (even for self-purchases)
                Notification.objects.create(
                    user=product.user,
                    title="New Sale!",
                    message=f"Your product '{product.title}' has been purchased by {request.user.username}. Quantity: {item.quantity}"
                )
            
            # Clear cart items
            cart_items = Cart.objects.filter(user=request.user)
            cart_items.delete()
            
            # Create notification for buyer
            Notification.objects.create(
                user=request.user,
                title="Payment Successful!",
                message=f"Your payment for order #{order.id} was successful. Transaction ID: {transaction_id}"
            )
            
            # Success message based on payment method
            method_messages = {
                'credit_card': f"Credit card payment successful! Your transaction ID is {transaction_id}.",
                'upi': f"UPI payment successful! Your transaction ID is {transaction_id}.",
                'net_banking': f"Net banking payment successful! Your transaction ID is {transaction_id}."
            }
            
            success_message = method_messages.get(
                payment_method, 
                f"Payment successful! Your transaction ID is {transaction_id}."
            )
            
            messages.success(request, success_message)
            return redirect('order_success', order_id=order_id)
        else:
            # Update order payment status to failed
            order.payment_status = 'FAILED'
            order.save()
            
            # Create notification for payment failure
            Notification.objects.create(
                user=request.user,
                title="Payment Failed",
                message=f"Your payment for order #{order.id} was not successful. Please try again."
            )
            
            # Failure message based on payment method
            failure_messages = {
                'credit_card': "Credit card payment failed. Please check your card details and try again.",
                'upi': "UPI payment failed. Please check your UPI ID and try again.",
                'net_banking': "Net banking payment failed. Please check your bank details and try again."
            }
            
            error_message = failure_messages.get(
                payment_method, 
                "Payment failed. Please try again or use a different payment method."
            )
            
            messages.error(request, error_message)
            return redirect('payment', order_id=order_id)
    
    return redirect('payment', order_id=order_id)


@login_required
def userprofile(request):
    context = {}
    
    # Get user's products (for sale items)
    products = ProductItem.objects.filter(user=request.user, post_type="FS").order_by('-create_date')
    context['products'] = products
    
    # Get user's orders (purchases) - Show all orders, not just completed ones
    orders = Order.objects.filter(user=request.user).order_by('-create_date')
    
    # Debug: Log the orders found for the current user
    print(f"Found {orders.count()} orders for user {request.user.id} ({request.user.username})")
    for order in orders:
        print(f"Order #{order.id}, Payment Status: {order.payment_status}, Status: {order.status}")
    
    context['orders'] = orders
    
    # Get product messages
    beats = BeatItem.objects.filter(product__user=request.user).order_by('-create_date')
    context['beats'] = beats
    
    # Get notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-create_date')[:10]
    context['notifications'] = notifications
    
    # Calculate dashboard statistics
    total_products = products.count()
    # Count products that have sold at least one unit
    sold_products = sum(1 for product in products if product.sold_quantity > 0)
    # Count products that are active (have available quantity)
    active_listings = sum(1 for product in products if product.quantity > product.sold_quantity)
    
    context['total_products'] = total_products
    context['sold_products'] = sold_products
    context['active_listings'] = active_listings
    
    # Get user profile if it exists
    if hasattr(request.user, 'userprofile'):
        context['profile'] = request.user.userprofile
    
    return render(request, 'account/dashboard.html', context)


def project(request):
    """
    Render the project information page
    """
    return render(request, 'project.html')


# Add quantity to existing product
@login_required
def add_quantity(request, product_id):
    product = get_object_or_404(ProductItem, id=product_id, user=request.user)
    
    if request.method == 'POST':
        additional_quantity = request.POST.get('additional_quantity')
        try:
            additional_quantity = float(additional_quantity)
            if additional_quantity <= 0:
                messages.error(request, "Please enter a positive quantity.")
                return redirect('userprofile')
                
            # Add the additional quantity
            product.quantity += additional_quantity
            product.save()
            
            messages.success(request, f"Successfully added {additional_quantity} {product.get_unit_display()} to {product.title}.")
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title="Product Quantity Updated",
                message=f"You've added {additional_quantity} {product.get_unit_display()} to {product.title}."
            )
            
        except ValueError:
            messages.error(request, "Please enter a valid number for quantity.")
    
    return redirect('userprofile')


# Custom context processor for cart count
def get_cart_count(request):
    """Get the cart count for the current user"""
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    return {'cart_count': cart_count}


@login_required
def add_review(request, product_id):
    product = get_object_or_404(ProductItem, pk=product_id)
    
    # Check if user has already reviewed this product
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, "You have already reviewed this product.")
        return redirect('detail', id=product_id)
    
    # Check if user has purchased this product
    has_purchased = Order.objects.filter(
        user=request.user, 
        status='COMPLETED', 
        orderitem__product=product
    ).exists()
    
    if not has_purchased:
        messages.warning(request, "You can only review products you have purchased.")
        return redirect('detail', id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if not rating:
            messages.error(request, "Please provide a rating.")
            return redirect('detail', id=product_id)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect('detail', id=product_id)
        
        # Create the review
        review = Review(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        review.save()
        
        messages.success(request, "Your review has been added successfully.")
        return redirect('detail', id=product_id)
    
    # If GET request, redirect to product detail
    return redirect('detail', id=product_id)
