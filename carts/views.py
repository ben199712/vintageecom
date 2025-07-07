from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
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
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'store/cart.html',context)
