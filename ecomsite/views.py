from django.shortcuts import render
from store.models import Product

def home(request):
    coming_soon_products = Product.objects.filter(is_available=True, coming_soon=True).order_by('-modified_date')[:12]
    products = Product.objects.filter(is_available=True).order_by('-modified_date')[:12]
    

    context = {
        'products': products,
        'coming_soon_products': coming_soon_products,
    }
    return render(request, 'index.html', context)

def contact(request):
    return render(request, 'contact.html')