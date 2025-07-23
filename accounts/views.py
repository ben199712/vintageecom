from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import Account
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

# Create your views here.

def register(request):
    if request.method == 'POST':
        print("POST request received")  # Debug
        print(f"CSRF token in POST: {'csrfmiddlewaretoken' in request.POST}")  # Debug
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            # Add success message
            messages.success(request, f'Registration successful! Welcome {first_name}! You can now log in with your credentials.')
            return redirect('login')  # or wherever you want to redirect
        else:
            print(f"Form errors: {form.errors}")  # Debug
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Please enter both email and password')
            return redirect('login')

        try:
            user = Account.objects.get(email=email)
            if user.check_password(password):
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('login')
        except Account.DoesNotExist:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    # Import here to avoid circular imports
    from orders.models import Order, Payment
    from carts.models import Cart, CartItem
    from carts.views import cart_id
    from django.db.models import Sum, Count, Q

    # Get user's orders
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Calculate statistics
    total_orders = user_orders.count()
    completed_orders = user_orders.filter(status='delivered').count()

    # Calculate total spent (only for paid orders)
    total_spent = user_orders.filter(
        payment_status='paid'
    ).aggregate(
        total=Sum('order_total')
    )['total'] or 0

    # Get current cart count
    cart_count = 0
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0

    # Get recent orders (last 10)
    recent_orders = user_orders[:10]

    # Get payment history
    user_payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:10]

    # Prepare context data
    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'cart_count': cart_count,  # Real cart count
        'favorites_count': 0,  # You can implement wishlist later
        'recent_orders': recent_orders,
        'payments': user_payments,
    }

    return render(request, 'accounts/dashboard.html', context)


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        if not email:
            messages.error(request, 'Please enter your email address')
            return redirect('forgotpassword')

        try:
            user = Account.objects.get(email=email)
            # Send reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            email_message = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            email_message.send()
            messages.success(request, f'Password reset instructions have been sent to {email}')
            return redirect('login')  # or wherever you want to redirect
        except Account.DoesNotExist:
            messages.error(request, 'No account found with that email address')
            return redirect('forgotpassword')

    return render(request, 'accounts/forgotpassword.html')

