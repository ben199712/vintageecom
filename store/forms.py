from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full name',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Your Full name'"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Email Address'"
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Subject',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Enter Subject'"
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Message',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Enter Message'"
            }),
        }
