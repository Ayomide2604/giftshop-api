from .models import Order, OrderItem


def place_order(user):
    cart = getattr(user, 'cart', None)

    if not cart or not cart.items.exists():
        raise ValueError("Cart is empty. Add items before placing an order.")

    # Create an order
    order = Order.objects.create(user=user)

    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            content_type=cart_item.content_type,
            object_id=cart_item.object_id,
            quantity=cart_item.quantity,
            price=getattr(cart_item.item, 'price', 0)
        )

    order.calculate_total_price()  # Update total price
    cart.items.all().delete()  # Clear cart items
    cart.delete()  # Delete the cart

    return order
