from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from ..models import Product, Sale, SaleItem, Customer
from ..utils.discounts import calculate_discounted_price


def cart_view(request):
    cart = request.session.get("pos_cart", {})
    items = []
    total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        price, _, _ = calculate_discounted_price(product)
        total += price * qty

        items.append({"product": product, "qty": qty, "price": price})

    return render(request, "cashier/cart.html", {
        "items": items,
        "total": total
    })


@transaction.atomic
def process_sale(request):
    if request.method != "POST":
        return redirect("checkout")

    cart = request.session.get("cart", {})

    full_name = request.POST.get("full_name")
    phone = request.POST.get("phone")
    payment_method = request.POST.get("payment_method")

    # ✅ FIX: safe customer creation (NO duplicates error)
    customer = Customer.objects.filter(phone=phone).first()

    if not customer:
        customer = Customer.objects.create(
            full_name=full_name or "Walk-in Customer",
            phone=phone
        )
    else:
        # update name if empty
        if full_name and not customer.full_name:
            customer.full_name = full_name
            customer.save()

    sale = Sale.objects.create(
        customer=customer,
        payment_method=payment_method,
        status="completed"
    )

    subtotal = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        price = float(product.selling_price or 0)
        line_total = price * qty

        subtotal += line_total

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=qty,
            unit_price=price,
            line_total=line_total
        )

        product.stock_qty = (product.stock_qty or 0) - qty
        product.save()

    sale.subtotal = subtotal
    sale.total_amount = subtotal
    sale.save()

    request.session["cart"] = {}

    return redirect("dashboard")


def checkout_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        price, _, _ = calculate_discounted_price(product)
        total += price * qty

        items.append({"product": product, "qty": qty, "price": price})

    return render(request, "user/checkout.html", {
        "items": items,
        "total": total
    })
