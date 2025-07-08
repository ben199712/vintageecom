from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import Account

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
    return render(request, 'accounts/dashboard.html')
