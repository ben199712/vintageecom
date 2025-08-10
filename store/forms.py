from django import forms
from .models import Contact, Review

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


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['subject', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter review subject (optional)',
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Enter review subject (optional)'"
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review here...',
                'rows': 4,
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Write your review here...'"
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)])
        }

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['subject'].required = False
        self.fields['review'].required = True
        self.fields['rating'].required = True
