from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, timedelta

from accounts.models import Account
from store.models import Product
from orders.models import Order, OrderItem, Payment


class Command(BaseCommand):
    help = 'Create sample orders for testing dashboard functionality'

    def handle(self, *args, **options):
        # Get the first user (you can modify this to target specific users)
        try:
            user = Account.objects.filter(is_active=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No active users found. Please create a user first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding user: {e}'))
            return

        # Get some products (create dummy ones if none exist)
        products = list(Product.objects.all()[:5])
        if not products:
            self.stdout.write(self.style.WARNING('No products found. Creating sample products...'))
            # Create sample products if none exist
            from category.models import Category
            category, created = Category.objects.get_or_create(
                category_name='Electronics',
                defaults={'slug': 'electronics', 'description': 'Electronic items'}
            )
            
            sample_products = [
                {'product_name': 'Wireless Headphones', 'price': 149.99},
                {'product_name': 'Bluetooth Speaker', 'price': 89.99},
                {'product_name': 'Phone Case', 'price': 29.99},
                {'product_name': 'USB Cable', 'price': 14.99},
                {'product_name': 'Screen Protector', 'price': 19.99},
            ]
            
            for product_data in sample_products:
                product, created = Product.objects.get_or_create(
                    product_name=product_data['product_name'],
                    defaults={
                        'slug': product_data['product_name'].lower().replace(' ', '-'),
                        'description': f"High quality {product_data['product_name']}",
                        'price': product_data['price'],
                        'stock': 100,
                        'is_available': True,
                        'category': category,
                    }
                )
                products.append(product)

        # Create sample orders
        order_statuses = ['pending', 'processing', 'shipped', 'delivered']
        payment_statuses = ['pending', 'paid', 'failed']
        payment_methods = ['credit_card', 'paypal', 'bank_transfer']

        for i in range(5):  # Create 5 sample orders
            # Create order
            order_number = f"ORD-2024-{str(i+1).zfill(3)}"
            
            # Random date within last 30 days
            random_days = random.randint(1, 30)
            order_date = timezone.now() - timedelta(days=random_days)
            
            order = Order.objects.create(
                user=user,
                order_number=order_number,
                first_name=user.first_name or 'John',
                last_name=user.last_name or 'Doe',
                email=user.email,
                phone='1234567890',
                address_line_1='123 Main Street',
                address_line_2='Apt 4B',
                city='New York',
                state='NY',
                country='USA',
                order_total=Decimal('0.00'),  # Will calculate later
                tax=Decimal('0.00'),
                status=random.choice(order_statuses),
                payment_status=random.choice(payment_statuses),
                is_ordered=True,
                created_at=order_date,
            )

            # Add random items to order
            total_amount = Decimal('0.00')
            num_items = random.randint(1, 3)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                item_total = Decimal(str(product.price)) * quantity
                total_amount += item_total
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    product_price=product.price,
                    ordered=True,
                    created_at=order_date,
                )

            # Calculate tax (8% for example)
            tax_amount = total_amount * Decimal('0.08')
            final_total = total_amount + tax_amount

            # Update order totals
            order.order_total = final_total
            order.tax = tax_amount
            order.save()

            # Create payment record
            payment_id = f"TXN-2024-{str(i+1).zfill(3)}"
            Payment.objects.create(
                user=user,
                order=order,
                payment_id=payment_id,
                payment_method=random.choice(payment_methods),
                amount_paid=final_total,
                status='completed' if order.payment_status == 'paid' else order.payment_status,
                created_at=order_date,
            )

            self.stdout.write(
                self.style.SUCCESS(f'Created order {order_number} with {num_items} items - Total: ${final_total}')
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample orders!'))
