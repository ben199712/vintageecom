from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import Product, Category
from .models import Cart, CartItem

# Create your views here.
def cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=cart_id(request)
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()   
    return redirect('cart')

def add_cart_ajax(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            try:
                cart = Cart.objects.get(cart_id=cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id=cart_id(request)
                )
                cart.save()

            try:
                cart_item = CartItem.objects.get(product=product, cart=cart)
                cart_item.quantity += 1
                cart_item.save()
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
                cart_item.save()

            # Get updated cart count and total
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            cart_count = sum(item.quantity for item in cart_items)
            total = sum(item.product.price * item.quantity for item in cart_items)

            return JsonResponse({
                'success': True,
                'message': f'{product.product_name} added to cart successfully!',
                'cart_count': cart_count,
                'total': float(total),
                'product_name': product.product_name
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error adding to cart: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_ajax(request, product_id):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(cart_id=cart_id(request))
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(product=product, cart=cart)

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                message = f'Reduced {product.product_name} quantity'
            else:
                cart_item.delete()
                message = f'Removed {product.product_name} from cart'

            # Get updated cart data
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            cart_count = sum(item.quantity for item in cart_items)
            total = sum(item.product.price * item.quantity for item in cart_items)

            # Get updated item data
            try:
                updated_item = CartItem.objects.get(product=product, cart=cart)
                item_quantity = updated_item.quantity
                item_subtotal = updated_item.sub_total()
            except CartItem.DoesNotExist:
                item_quantity = 0
                item_subtotal = 0

            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart_count,
                'total': total,
                'item_quantity': item_quantity,
                'item_subtotal': item_subtotal,
                'item_removed': item_quantity == 0
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error updating cart'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def remove_cart_item_ajax(request, product_id):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(cart_id=cart_id(request))
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.delete()

            # Get updated cart data
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            cart_count = sum(item.quantity for item in cart_items)
            total = sum(item.product.price * item.quantity for item in cart_items)

            return JsonResponse({
                'success': True,
                'message': f'{product.product_name} removed from cart',
                'cart_count': cart_count,
                'total': total,
                'item_removed': True
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error removing item'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def remove_cart_item(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
    except Cart.DoesNotExist:
        pass  # Cart doesn't exist
    except CartItem.DoesNotExist:
        pass  # Cart item doesn't exist
    except Exception as e:
        print(f"Error removing cart item: {e}")  # For debugging
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        # Use session-based cart for all users
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

    except ObjectDoesNotExist:
        cart_items = []

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'store/cart.html', context)


def get_cart_count(request):
    """
    API endpoint to get current cart count
    """
    cart_count = 0
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0

    return JsonResponse({
        'success': True,
        'cart_count': cart_count
    })

def checkout(request, total=0, quantity=0, cart_items=None):
    """
    Complete checkout view that handles:
    1. Cart validation
    2. User authentication check
    3. Order form processing
    4. Tax calculation
    5. Order creation
    """

    # Get cart and calculate totals (use session-based cart for all users)
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    except Cart.DoesNotExist:
        cart_items = []

    # Calculate totals
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    # Calculate tax (8% for example)
    tax = (8 * total) / 100
    grand_total = total + tax

    # Check if cart is empty
    if not cart_items:
        messages.warning(request, 'Your cart is empty. Please add items before checkout.')
        return redirect('cart')

    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to proceed with checkout.')
        return redirect('login')

    # Handle form submission
    if request.method == 'POST':
        from orders.forms import OrderForm
        form = OrderForm(request.POST)

        if form.is_valid():
            # Create order
            from orders.models import Order, OrderItem, Payment
            import datetime

            # Generate order number
            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            day = int(datetime.date.today().strftime('%d'))
            date = datetime.date(year, month, day)
            current_date = date.strftime("%Y%m%d")

            order_number = current_date + str(total)

            # Create order instance
            order = Order()
            order.user = request.user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address_line_1 = form.cleaned_data['address_line_1']
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.order_number = order_number
            order.order_total = grand_total
            order.tax = tax
            order.save()

            # Create order items
            for item in cart_items:
                order_item = OrderItem()
                order_item.order = order
                order_item.product = item.product
                order_item.quantity = item.quantity
                order_item.product_price = item.product.price
                order_item.ordered = True
                order_item.save()

            # Store order in session for payment processing
            request.session['order_id'] = order.id

            messages.success(request, 'Order placed successfully! Please proceed with payment.')
            return redirect('payment')

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        # Pre-fill form with user data if available
        from orders.forms import OrderForm
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': getattr(request.user, 'phone_number', ''),
            }
        form = OrderForm(initial=initial_data)

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'form': form,
    }

    return render(request, 'store/checkout.html', context)


def payment(request):
    """
    Payment processing view
    """
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'No order found. Please place an order first.')
        return redirect('checkout')

    try:
        from orders.models import Order
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('checkout')

    context = {
        'order': order,
    }

    return render(request, 'store/payment.html', context)


def payment_success(request):
    import os
    import requests
    tx_ref = request.GET.get('tx_ref') or request.session.get('tx_ref')
    order_id = request.session.get('order_id')
    if not order_id or not tx_ref:
        messages.error(request, 'No order or transaction reference found.')
        return redirect('store')

    # Verify payment with Flutterwave
    secret_key = os.getenv('SECRET_KEY')
    verify_url = f'https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}'
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(verify_url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        status = result.get('status')
        data = result.get('data', {})
        payment_status = data.get('status')
        amount_paid = data.get('amount')
        payment_id = data.get('id')
        payment_method = data.get('payment_type', 'card')
        if status == 'success' and payment_status == 'successful':
            try:
                from orders.models import Order, Payment
                order = Order.objects.get(id=order_id, user=request.user)
                order.is_ordered = True
                order.status = 'processing'
                order.payment_status = 'paid'
                order.save()
                Payment.objects.create(
                    user=request.user,
                    order=order,
                    payment_id=payment_id,
                    payment_method=payment_method,
                    amount_paid=amount_paid,
                    status='completed'
                )
                # Clear cart
                try:
                    from carts.models import Cart, CartItem, cart_id
                    cart = Cart.objects.get(cart_id=cart_id(request))
                    CartItem.objects.filter(cart=cart).delete()
                except Exception:
                    pass
                # Clear session
                for key in ['order_id', 'tx_ref']:
                    if key in request.session:
                        del request.session[key]
                messages.success(request, f'Payment successful! Your order #{order.order_number} has been placed.')
                return redirect('order_complete', order_number=order.order_number)
            except Exception as e:
                messages.error(request, f'Order processing error: {e}')
                return redirect('store')
        else:
            messages.error(request, 'Payment not successful or incomplete.')
            return redirect('store')
    else:
        messages.error(request, 'Could not verify payment with Flutterwave.')
        return redirect('store')


def order_complete(request, order_number):
    """
    Order completion page
    """
    try:
        from orders.models import Order
        order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=True)

        context = {
            'order': order,
        }

        return render(request, 'store/order_complete.html', context)

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('store')
