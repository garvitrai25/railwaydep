from django.contrib import admin
from django.utils.html import format_html

from .models import (BeatItem, Cart, Category, Complain, ContactUs,
                     EmailSubscription, Notification, Order, OrderItem,
                     ProductItem, Review)

admin.site.register(Category)
admin.site.register(BeatItem)
admin.site.register(Complain)
admin.site.register(ContactUs)
admin.site.register(EmailSubscription)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(Notification)


@admin.register(ProductItem)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'title', 'price', 'category', 'unit', 'quantity', 'has_image']
    search_fields = ('title', 'price', 'category', 'unit', 'quantity')
    list_editable = ['title', 'price', 'category', 'unit', 'quantity']
    list_display_links = ['pk', 'user']
    readonly_fields = ['image_preview']
    fields = ['user', 'category', 'title', 'description', 'image', 'image_preview', 'price', 'quantity', 'sold_quantity', 'unit', 'post_type', 'status']
    
    def has_image(self, obj):
        if obj.image:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    
    has_image.short_description = 'Image'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" />', obj.image.url)
        return format_html('<p style="color: red;">No image available. Please add an image.</p>')
    
    image_preview.short_description = 'Image Preview'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'verified_purchase', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'created_at']
    search_fields = ['product__title', 'user__username', 'comment']
    readonly_fields = ['verified_purchase']
