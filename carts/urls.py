from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('add_cart_ajax/<int:product_id>/', views.add_cart_ajax, name='add_cart_ajax'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_ajax/<int:product_id>/', views.remove_cart_ajax, name='remove_cart_ajax'),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('remove_cart_item_ajax/<int:product_id>/', views.remove_cart_item_ajax, name='remove_cart_item_ajax'),

    path('checkout/', views.checkout, name='checkout'),
    
]
