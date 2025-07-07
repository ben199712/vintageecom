from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control',
        'onfocus': "this.placeholder = ''",
        'onblur': "this.placeholder = 'Password'"
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control',
        'onfocus': "this.placeholder = ''",
        'onblur': "this.placeholder = 'Confirm Password'"
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'form-control',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'First Name'"
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'form-control',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Last Name'"
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'form-control',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Username'"
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'class': 'form-control',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Email Address'"
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'form-control',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Phone Number'"
            }),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return confirm_password

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data