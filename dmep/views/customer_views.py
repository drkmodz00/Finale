import json
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator


from ..models import Product, Customer, Sale, SaleItem, Discount, Category
from ..utils.discounts import calculate_discounted_price


# =====================
# DASHBOARD
# =====================
def dashboard(request):
    products = Product.objects.filter(status="active")[:8]
    return render(request, "user/dashboard.html", {"products": products})


# =====================
# PRODUCTS
# =====================
def product_list(request):
    q = request.GET.get("q", "")
    category_id = request.GET.get("category")

    products = Product.objects.filter(status="active")

    selected_category = category_id
    active_parent_id = None

    # SEARCH
    if q:
        products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q))

    # CATEGORY FILTER
    if category_id:
        products = products.filter(category_id=category_id)

        try:
            selected_cat = Category.objects.get(id=category_id)
            active_parent_id = selected_cat.parent_id
        except Category.DoesNotExist:
            pass

    # ✅ ATTACH DISCOUNT TO EACH PRODUCT
    product_list = []
    for product in products:
        final_price, discount_obj, percent = calculate_discounted_price(product)

        product.final_price = final_price
        product.discount_percent = percent or 0
        product.discount_obj = discount_obj

        product_list.append(product)

    # PAGINATION
    paginator = Paginator(product_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(parent__isnull=True).prefetch_related("subcategories")

    return render(request, "user/product/list.html", {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "categories": categories,
        "q": q,
        "selected_category": selected_category,
        "active_parent_id": active_parent_id,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    price, discount, percent = calculate_discounted_price(product)

    return JsonResponse({
        "id": product.id,
        "name": product.name,
        "price": float(price),
        "stock": product.stock_qty,
    })


def product_search(request):
    q = request.GET.get("q", "")
    results = Product.objects.filter(name__icontains=q)
    return render(request, "user/search.html", {"results": results})


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
# REMOVE ITEM
# =====================
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =====================
# CLEAR CART
# =====================
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    return redirect("cart")

# =====================
# CHECKOUT
# =====================
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

# =====================
# PROCESS SALE (CUSTOMER)
# =====================
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