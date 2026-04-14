from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction

from ..models import *
from ..utils.discounts import calculate_discounted_price


# =========================
# POS CHECKOUT
# =========================

def cart_view(request):
    cart = request.session.get("cart", {})

    items = []
    total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)

        price, _, _ = calculate_discounted_price(product)
        qty = int(qty)

        total += price * qty

        items.append({
            "product": product,
            "qty": qty,
            "price": price,
        })

    return render(request, "cashier/cart.html", {
        "items": items,
        "total": total
    })


# =========================
# PROCESS SALE
# =========================

@transaction.atomic
def process_sale(request):
    if request.method != "POST":
        return redirect("cart")

    cart = request.session.get("cart", {})

    customer, _ = Customer.objects.get_or_create(
        full_name=request.POST.get("name"),
        phone=request.POST.get("phone")
    )

    sale = Sale.objects.create(
        customer=customer,
        subtotal=0,
        total_amount=0,
        status="completed"
    )

    subtotal = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        price, _, _ = calculate_discounted_price(product)

        line_total = price * qty
        subtotal += line_total

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=qty,
            unit_price=price,
            line_total=line_total
        )

        # stock update
        product.stock_qty = (product.stock_qty or 0) - qty
        product.save()

    sale.subtotal = subtotal
    sale.total_amount = subtotal
    sale.save()

    request.session["cart"] = {}

    return redirect("cart")