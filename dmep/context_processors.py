def cart_count(request):
    cart = request.session.get('cart', {})
    return {
        'cart_count': sum(item['qty'] for item in cart.values())
    }