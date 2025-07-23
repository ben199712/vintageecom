from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Form for collecting billing and shipping information during checkout
    """
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address_line_1', 'address_line_2', 'city', 'state', 'country'
        ]
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        
        # Add CSS classes and placeholders to form fields
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'First Name',
            'required': True
        })
        
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Last Name',
            'required': True
        })
        
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email Address',
            'type': 'email',
            'required': True
        })
        
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'required': True
        })
        
        self.fields['address_line_1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Address Line 1',
            'required': True
        })
        
        self.fields['address_line_2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Address Line 2 (Optional)'
        })
        
        self.fields['city'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'City',
            'required': True
        })
        
        self.fields['state'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'State/Province',
            'required': True
        })
        
        self.fields['country'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Country',
            'required': True
        })
        
        # Make all fields required except address_line_2
        for field_name, field in self.fields.items():
            if field_name != 'address_line_2':
                field.required = True
