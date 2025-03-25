from django.urls import path

from .views import (add_complain, add_product, add_quantity, add_review,
                    add_to_cart, buy_page, checkout, contact, delete_product,
                    detail, edit_product, email_subscribe, home,
                    mark_notification_as_read, my_orders, order_detail,
                    order_success, payment, process_payment, remove_from_cart,
                    reply, sale_page, update_cart, view_cart, confirm_order,
                    cancel_order, product_orders)

urlpatterns = [
    path('', home, name='home'),
    path('add-product/', add_product, name='add_product'),
    path('edit-product/<int:id>/', edit_product, name='edit_product'),
    path('delete-product/<int:id>/', delete_product, name='delete_product'),
    path('add-quantity/<int:product_id>/', add_quantity, name='add_quantity'),
    path('product/<int:product_id>/orders/', product_orders, name='product_orders'),
    path('sale-page/', sale_page, name='sale_page'),
    path('buy-page/', buy_page, name='buy_page'),
    path('reply/', reply, name='reply'),
    path('detail/<int:id>/', detail, name='detail'),
    path('contact/', contact, name='contact'),
    path('email-subscribe/', email_subscribe, name='email_subscribe'),
    path('add-complain/', add_complain, name='add_complain'),
    
    # Cart URLs
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('update-cart/<int:cart_id>/', update_cart, name='update_cart'),
    path('remove-from-cart/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    
    # Checkout and Order URLs
    path('checkout/', checkout, name='checkout'),
    path('payment/<int:order_id>/', payment, name='payment'),
    path('process-payment/<int:order_id>/', process_payment, name='process_payment'),
    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('my-orders/', my_orders, name='my_orders'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order/<int:order_id>/confirm/', confirm_order, name='confirm_order'),
    path('order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    
    # Review URL
    path('add-review/<int:product_id>/', add_review, name='add_review'),
    
    # Notification URL
    path('mark-notification-as-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
]
