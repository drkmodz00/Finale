def cart_count(request):
    cart = request.session.get('cart', {})
    total = sum(int(qty) for qty in cart.values())
    return {'cart_count': total}

# dmep/context_processors.py
from .models import Category

def categories(request):
    return {
        "categories": Category.objects.all()
    }