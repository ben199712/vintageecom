from django.core.management.base import BaseCommand
from carts.models import CartItem
from store.models import Product


class Command(BaseCommand):
    help = 'Clean up invalid cart items'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up cart items...')
        
        # Get all cart items
        cart_items = CartItem.objects.all()
        total_items = cart_items.count()
        invalid_items = 0
        
        self.stdout.write(f'Found {total_items} cart items to check')
        
        for item in cart_items:
            try:
                # Check if product exists and has price
                if not item.product:
                    self.stdout.write(f'Deleting cart item {item.id} - no product')
                    item.delete()
                    invalid_items += 1
                elif not hasattr(item.product, 'price'):
                    self.stdout.write(f'Deleting cart item {item.id} - product has no price')
                    item.delete()
                    invalid_items += 1
                elif not isinstance(item.quantity, int) or item.quantity <= 0:
                    self.stdout.write(f'Deleting cart item {item.id} - invalid quantity: {item.quantity}')
                    item.delete()
                    invalid_items += 1
                else:
                    # Test the calculation
                    test_total = item.product.price * item.quantity
                    self.stdout.write(f'Cart item {item.id} is valid - Product: {item.product.product_name}, Price: {item.product.price}, Qty: {item.quantity}')
                    
            except Exception as e:
                self.stdout.write(f'Error with cart item {item.id}: {e}')
                self.stdout.write(f'Deleting problematic cart item {item.id}')
                item.delete()
                invalid_items += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleanup complete! Removed {invalid_items} invalid items out of {total_items} total items.')
        )
