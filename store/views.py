from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Product, Category, Review
from carts.models import CartItem
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Min, Max, Avg
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm, ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

    # Get price filter parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'default')

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)

    # Apply price filtering
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=int(max_price))

    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('product_name')
    elif sort_by == 'name_desc':
        products = products.order_by('-product_name')
    elif sort_by == 'newest':
        products = products.order_by('-created_date')
    else:
        products = products.order_by('id')  # default sorting

    # Get price range for the filter
    all_products = Product.objects.filter(is_available=True)
    if category_slug:
        all_products = all_products.filter(category=categories)

    price_range = all_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    product_count = products.count()

    # Pagination
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    # Add deals of the week products
    deals_week_products = Product.objects.filter(is_available=True, week_Deals=True).order_by('-modified_date')[:6]

    context = {
        'products': paged_products,
        'categories': categories,
        'product_count': product_count,
        'deals_week_products': deals_week_products,
        'price_range': price_range,
        'current_min_price': min_price or price_range['min_price'],
        'current_max_price': max_price or price_range['max_price'],
        'current_sort': sort_by,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=request.session.session_key, product=single_product).exists()  # Check if the product is in the cart
    except Exception as e :
        raise e

    # Get reviews for this product
    reviews = Review.objects.filter(product=single_product, status=True).order_by('-created_at')

    # Calculate review statistics
    review_count = reviews.count()
    if review_count > 0:
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        average_rating = round(average_rating, 1) if average_rating else 0

        # Count ratings by star
        rating_counts = {}
        for i in range(1, 6):
            rating_counts[i] = reviews.filter(rating=i).count()
    else:
        average_rating = 0
        rating_counts = {i: 0 for i in range(1, 6)}

    # Check if user has already reviewed this product
    user_review = None
    can_review = False
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=single_product, user=request.user)
        except Review.DoesNotExist:
            # Check if user has purchased this product (optional - you can remove this check)
            can_review = True

    # Add deals of the week products for product detail page too
    deals_week_products = Product.objects.filter(is_available=True, week_Deals=True).order_by('-modified_date')[:6]

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'deals_week_products': deals_week_products,
        'reviews': reviews,
        'review_count': review_count,
        'average_rating': average_rating,
        'rating_counts': rating_counts,
        'user_review': user_review,
        'can_review': can_review,
        'review_form': ReviewForm(),
    }
    return render(request, 'store/product_detail.html', context)


@login_required(login_url='login')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # Check if user has already reviewed this product
            review = Review.objects.get(user=request.user, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated.')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Review.DoesNotExist:
            # Create new review
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = Review()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user = request.user
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
            else:
                messages.error(request, 'Please correct the errors below.')

    return redirect(url)

def search(request):
    products = None
    product_count = 0

    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            products = Product.objects.order_by('-created_date').filter(Q(product_name__icontains=q))

            # Apply price filtering to search results
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')

            if min_price and min_price.isdigit():
                products = products.filter(price__gte=int(min_price))
            if max_price and max_price.isdigit():
                products = products.filter(price__lte=int(max_price))

            product_count = products.count()

    # Get price range for search results
    all_products = Product.objects.filter(is_available=True)
    price_range = all_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    # Add deals of the week products for search page too
    deals_week_products = Product.objects.filter(is_available=True, week_Deals=True).order_by('-modified_date')[:6]

    context = {
        'products': products,
        'product_count': product_count,
        'deals_week_products': deals_week_products,
        'price_range': price_range,
        'current_min_price': request.GET.get('min_price', price_range['min_price']),
        'current_max_price': request.GET.get('max_price', price_range['max_price']),
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
    print(f"DEBUG: Generated tx_ref = {tx_ref}")
    print(f"DEBUG: Stored tx_ref in session = {request.session.get('tx_ref')}")

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
        'redirect_url': request.build_absolute_uri(f'/cart/payment-success/?tx_ref={tx_ref}'),
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
    print(f"DEBUG: Flutterwave payment data = {payment_data}")  # Debug
    response = requests.post(endpoint, headers=headers, data=json.dumps(payment_data))
    print(f"DEBUG: Flutterwave response status = {response.status_code}")
    if response.status_code in [200, 201]:
        payment_respond = response.json()
        print(f"DEBUG: Flutterwave response = {payment_respond}")  # Debug
        payment_link = payment_respond.get('data', {}).get('link')
        if payment_link:
            return redirect(payment_link)
        else:
            return HttpResponse('Payment link not returned by Flutterwave.', status=400)
    else:
        return HttpResponse(f'Payment failed: {response.text}', status=400)
