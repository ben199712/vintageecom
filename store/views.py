from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Category
from carts.models import CartItem
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.contrib import messages
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'categories': categories,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=request.session.session_key, product=single_product).exists()  # Check if the product is in the cart
    except Exception as e :
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,  
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            products = Product.objects.order_by('-created_date').filter(Q(product_name__icontains=q))
            product_count = products.count()
            
    context = {
        'products': products,
        'product_count': product_count,
    }
            
    return render(request, 'store/store.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'store/contact.html', {'form': form, 'success': True})
        else:
            return render(request, 'store/contact.html', {'form': form, 'success': False})

    return render(request, 'store/contact.html', {'form': ContactForm()})



def make_payment(request):
    import uuid
    from decimal import Decimal
    from carts.models import Cart, CartItem

    public_key = os.getenv('PUBLIC_KEY')
    secret_key = os.getenv('SECRET_KEY')

    try:
        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        amount = sum(item.product.price * item.quantity for item in cart_items)
    except Cart.DoesNotExist:
        return HttpResponse('No cart found.', status=400)

    if amount <= 0:
        return HttpResponse('Cart is empty.', status=400)

    tx_ref = str(uuid.uuid4())
    request.session['tx_ref'] = tx_ref  # Store for later verification

    if request.user.is_authenticated:
        customer_email = request.user.email
        customer_name = f"{request.user.first_name} {request.user.last_name}"
    else:
        customer_email = 'guest@example.com'
        customer_name = 'Guest User'

    payment_data = {
        'tx_ref': tx_ref,
        'amount': str(amount),
        'currency': 'NGN',
        'redirect_url': request.build_absolute_uri(f'/carts/payment-success/?tx_ref={tx_ref}'),
        'payment_options': 'card',
        'customer': {
            'email': customer_email,
            'name': customer_name,
        },
        'customizations': {
            'title': 'Ecomsite Payment',
            'description': 'Payment for items in cart',
        },
    }

    endpoint = 'https://api.flutterwave.com/v3/payments'
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint, headers=headers, data=json.dumps(payment_data))
    if response.status_code in [200, 201]:
        payment_respond = response.json()
        payment_link = payment_respond.get('data', {}).get('link')
        if payment_link:
            return redirect(payment_link)
        else:
            return HttpResponse('Payment link not returned by Flutterwave.', status=400)
    else:
        print('SECRET_KEY:', secret_key)
        return HttpResponse(f'Payment failed: {response.text}', status=400)
