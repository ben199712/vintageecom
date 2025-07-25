from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from carts.models import CartItem
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

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
