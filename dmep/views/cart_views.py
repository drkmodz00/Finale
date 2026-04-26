from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from ..models import Product
from ..utils.discounts import calculate_discounted_price


def cart_view(request):
    cart = request.session.get("cart", {})
    selected_keys = request.session.get("selected_items")

    if selected_keys is None:
        selected_keys = list(cart.keys())
        request.session["selected_items"] = selected_keys

    cart = {str(k): v for k, v in cart.items()}
    selected_keys = set(str(k) for k in selected_keys)

    cart_items = []
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        # discount price
        final_price, _, _ = calculate_discounted_price(product)

        final_price = Decimal(str(final_price))
        selling_price = Decimal(str(product.selling_price or 0))

        line_original = selling_price * qty
        line_final = final_price * qty
        line_discount = line_original - line_final

        is_selected = pid in selected_keys

        if is_selected:
            subtotal += line_original
            discount_total += line_discount

        cart_items.append({
            "key": pid,
            "name": product.name,
            "image": product.img.url if product.img and product.img.name else None,
            "price": final_price,
            "qty": qty,
            "total": line_final,
            "discount": line_discount,
            "selected": is_selected,
        })

    total_amount = subtotal - discount_total

    return render(request, "user/cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount_total": discount_total,
        "total_amount": total_amount,
    })

def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =====================
# UPDATE CART QTY
# =====================
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
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart    
    })

# =====================
# REMOVE ITEM
# =====================
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
    })

# =====================
# CLEAR CART
# =====================
def clear_cart(request):
    request.session["cart"] = {}
    request.session["selected_items"] = []
    request.session.modified = True

    return redirect("cart")


