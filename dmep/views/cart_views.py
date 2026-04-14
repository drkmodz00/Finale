from django.shortcuts import redirect
from django.http import JsonResponse


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart[str(product_id)] = int(cart.get(str(product_id), 0)) + 1

    request.session["cart"] = cart
    return redirect("cart")


def update_cart(request, product_id, action):
    cart = request.session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        if action == "increase":
            cart[pid] += 1
        elif action == "decrease":
            cart[pid] -= 1

        if cart[pid] <= 0:
            del cart[pid]

    request.session["cart"] = cart
    return JsonResponse({"status": "ok"})


def clear_cart(request):
    request.session["cart"] = {}
    return redirect("cart")