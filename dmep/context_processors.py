def cart_count(request):
    cart = request.session.get('cart', {})

    total = 0
    for item in cart.values():
        if isinstance(item, dict):
            total += int(item.get("qty", 0))
        else:
            total += int(item)

    return {'cart_count': total}
        
# dmep/context_processors.py
from .models import Category

def categories(request):
    return {
        "categories": Category.objects.all()
    }