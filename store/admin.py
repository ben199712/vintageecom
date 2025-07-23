from django.contrib import admin
from .models import Product, Contact

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available', 'coming_soon')
    prepopulated_fields = {"slug": ('product_name',)}

admin.site.register(Product, ProductAdmin)
admin.site.register(Contact)
