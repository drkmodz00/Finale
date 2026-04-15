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
    selected_keys = request.session.get("selected_items", list(cart.keys()))

    full_name = request.POST.get("full_name") or "Walk-in Customer"
    phone = request.POST.get("phone")
    payment_method = request.POST.get("payment_method")

    customer = Customer.objects.filter(phone=phone).first()

    if customer:
        if full_name and customer.full_name != full_name:
            customer.full_name = full_name
            customer.save()
    else:
        customer = Customer.objects.create(
            full_name=full_name,
            phone=phone
        )

    sale = Sale.objects.create(
        customer=customer,
        payment_method=payment_method,
        status="completed"
    )

    subtotal = 0
    discount_total = 0

    for pid, qty in cart.items():
        if pid not in selected_keys:
            continue  # ✅ ONLY SELECTED

        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        final_price, _, _ = calculate_discounted_price(product)

        price = float(product.selling_price or 0)
        discounted_price = float(final_price)

        line_original = price * qty
        line_final = discounted_price * qty
        line_discount = line_original - line_final

        subtotal += line_original
        discount_total += line_discount

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=qty,
            unit_price=discounted_price,
            line_total=line_final
        )

        product.stock_qty = (product.stock_qty or 0) - qty
        product.save()

    sale.subtotal = subtotal
    sale.total_amount = subtotal - discount_total
    sale.save()

    request.session["cart"] = {}
    request.session["selected_items"] = []

    messages.success(request, "Order placed successfully!")
    return redirect("dashboard")

def checkout_view(request):
    cart = request.session.get("cart", {})
    selected_keys = request.session.get("selected_items", list(cart.keys()))

    cart_items = []
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")

    for pid, qty in cart.items():
        if pid not in selected_keys:
            continue  # ✅ ONLY SELECTED

        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        final_price, _, _ = calculate_discounted_price(product)
        final_price = Decimal(final_price)

        selling_price = Decimal(product.selling_price or 0)

        line_original = selling_price * qty
        line_final = final_price * qty
        line_discount = line_original - line_final

        subtotal += line_original
        discount_total += line_discount

        cart_items.append({
            "product": product,
            "qty": qty,
            "price": final_price,
            "discount_amount": line_discount,
        })

    payment_choices = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("gcash", "GCash"),
        ("maya", "Maya"),
    ]

    return render(request, "user/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount_total": discount_total,
        "total_amount": subtotal - discount_total,
        "payment_choices": payment_choices,
    })