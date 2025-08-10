from django.contrib import admin
from .models import Product, Contact, Review

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available', 'coming_soon', 'week_Deals')
    prepopulated_fields = {"slug": ('product_name',)}

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('product__product_name', 'user__first_name', 'user__last_name', 'subject')
    readonly_fields = ('ip', 'created_at', 'updated_at')

admin.site.register(Product, ProductAdmin)
admin.site.register(Contact)
admin.site.register(Review, ReviewAdmin)
