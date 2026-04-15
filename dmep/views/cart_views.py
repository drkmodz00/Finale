from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from ..models import Product
from ..utils.discounts import calculate_discounted_price


# =====================
# CART VIEW (FULL FIXED)
# =====================
def cart_view(request):
    cart = request.session.get("cart", {})
    selected_keys = request.session.get("selected_items", list(cart.keys()))

    cart_items = []
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        # ✅ APPLY DISCOUNT PROPERLY
        final_price, discount_obj, percent = calculate_discounted_price(product)
        final_price = Decimal(final_price)

        selling_price = Decimal(product.selling_price or 0)

        line_original = selling_price * qty
        line_final = final_price * qty
        line_discount = line_original - line_final

        # ✅ ONLY COUNT SELECTED ITEMS
        if pid in selected_keys:
            subtotal += line_original
            discount_total += line_discount

        cart_items.append({
            "key": pid,
            "name": product.name,
            "image": product.img.url if product.img else None,
            "price": final_price,
            "qty": qty,
            "total": line_final,
            "discount": line_discount,
            "selected": pid in selected_keys,  # 👈 important
        })

    return render(request, "user/cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount_total": discount_total,
        "total_amount": subtotal - discount_total,
    })
# =====================
# ADD TO CART
# =====================
def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =====================
# UPDATE CART
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

    return JsonResponse({"status": "ok"})


# =====================
# CLEAR CART
# =====================
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    return redirect("cart")