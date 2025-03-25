from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

POST_TYPE = (
    ("FS", "For Sale"),
    ("FB", "For Buy"),
)

ORDER_STATUS = (
    ("PENDING", "Pending"),
    ("PROCESSING", "Processing"),
    ("SHIPPED", "Shipped"),
    ("DELIVERED", "Delivered"),
    ("CANCELLED", "Cancelled"),
)

PAYMENT_STATUS = (
    ("PENDING", "Pending"),
    ("COMPLETED", "Completed"),
    ("FAILED", "Failed"),
    ("REFUNDED", "Refunded"),
)

PAYMENT_METHOD = (
    ("COD", "Cash On Delivery"),
    ("ONLINE", "Online Payment"),
)

class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class ProductItem(models.Model):
    POST_TYPE = (
        ('FS', 'For Sale'),
        ('FB', 'For Buy'),
    )
    
    UNIT_CHOICES = (
        ('piece', 'Piece'),
        ('set', 'Set'),
        ('unit', 'Unit'),
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    sold_quantity = models.FloatField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')
    post_type = models.CharField(max_length=2, choices=POST_TYPE)
    status = models.BooleanField(default=True)
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='locked_products')
    locked_until = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        """Returns whether the product is available for purchase"""
        return self.status and self.quantity > 0

    @property
    def available_quantity(self):
        """Returns the available quantity of the product"""
        return self.quantity - (self.sold_quantity or 0)

    @property
    def is_locked(self):
        """Returns whether the product is locked by a buyer"""
        if not self.locked_by or not self.locked_until:
            return False
        return timezone.now() < self.locked_until

    @property
    def average_rating(self):
        """Returns the average rating of the product"""
        reviews = self.review_set.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.sold_quantity > self.quantity:
            raise ValidationError('Sold quantity cannot be greater than total quantity')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def short_desc(self):
        return self.description[:200]

    def get_absolute_url(self):
        return reverse('detail', args=[str(self.id)])


class BeatItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    reply = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class Complain(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name_plural = "Contact Us Messages"


class EmailSubscription(models.Model):
    email = models.EmailField(unique=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    zipcode = models.CharField(max_length=10)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        # Ensure pincode and zipcode are synchronized
        if self.pincode and not self.zipcode:
            self.zipcode = self.pincode
        elif self.zipcode and not self.pincode:
            self.pincode = self.zipcode
        super().save(*args, **kwargs)

    def lock_products(self):
        """Lock the products for this order"""
        for item in self.orderitem_set.all():
            product = item.product
            product.locked_by = self.user
            product.locked_until = timezone.now() + timezone.timedelta(days=3)  # Lock for 3 days
            product.save()

    def unlock_products(self):
        """Unlock the products for this order"""
        for item in self.orderitem_set.all():
            product = item.product
            if product.locked_by == self.user:
                product.locked_by = None
                product.locked_until = None
                product.save()

    def confirm_order(self):
        """Confirm the order and mark products as sold"""
        self.status = 'PROCESSING'
        self.save()
        for item in self.orderitem_set.all():
            product = item.product
            product.sold_quantity += item.quantity
            product.locked_by = None
            product.locked_until = None
            product.save()

    def complete_order(self):
        """Mark the order as completed"""
        self.status = 'COMPLETED'
        self.save()

    def cancel_order(self):
        """Cancel the order and unlock products"""
        self.status = 'CANCELLED'
        self.save()
        self.unlock_products()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order.id} - {self.product.title}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)  # Keep for backwards compatibility
    updated_at = models.DateTimeField(auto_now=True)  # Keep for backwards compatibility
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    @property
    def total(self):
        return self.quantity * self.product.price


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=200, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ['-create_date']


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_purchase = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.product.title}"
        
    def save(self, *args, **kwargs):
        # Check if this is a verified purchase
        if not self.id:  # Only check on creation
            orders = Order.objects.filter(
                user=self.user, 
                status='COMPLETED', 
                orderitem__product=self.product
            )
            if orders.exists():
                self.verified_purchase = True
                
        super().save(*args, **kwargs)
    