def cart_count(request):
    cart = request.session.get('cart', {})

    total = 0

    for item in cart.values():
        if isinstance(item, dict):
            total += int(item.get("qty") or item.get("quantity") or 0)
        else:
            total += int(item or 0)

    return {'cart_count': total}