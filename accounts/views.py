from django.shortcuts import render, redirect
from django.contrib import messages
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
    return render(request, 'accounts/login.html')


def logout(request):
    return render(request, 'accounts/logout.html')