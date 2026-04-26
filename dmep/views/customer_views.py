import json, uuid
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from datetime import timedelta
from ..utils.utils import get_guest_id

from ..models import Product, Customer, Sale, SaleItem, Discount, Category, HelpCenter, NewsletterSubscriber
from ..utils.discounts import calculate_discounted_price


def dashboard(request):
    products = Product.objects.filter(status="active")
    last_order_code = request.session.pop('last_order_code', None)
    sale_products = []

    for product in products:
        final_price, discount_obj, percent = calculate_discounted_price(product)

        # attach values
        product.final_price = final_price
        product.discount_percent = percent or 0
        product.discount_obj = discount_obj

        if discount_obj:
            sale_products.append(product)

    sale_products = sale_products[:8]

    # categories (unchanged but cleaner fallback)
    women = Category.objects.filter(name__iexact="Women").first()
    men = Category.objects.filter(name__iexact="Men").first()
    kids = Category.objects.filter(name__iexact="Kids").first()

    return render(request, "customer/dashboard.html", {
        "sale_products": sale_products,
        "women_id": women.id if women else None,
        "men_id": men.id if men else None,
        "kids_id": kids.id if kids else None,
        "last_order_code": last_order_code,
    })

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
    if category_id in [None, "", "None"]:
        category_id = None

    if category_id:
        try:
            category_id = int(category_id)

            selected_cat = Category.objects.get(id=category_id)

            if selected_cat.parent is None:
                sub_ids = selected_cat.subcategories.values_list("id", flat=True)
                products = products.filter(
                    Q(category_id__in=sub_ids) | Q(category_id=selected_cat.id)
                )
            else:
                products = products.filter(category_id=selected_cat.id)

            active_parent_id = selected_cat.parent_id

        except Category.DoesNotExist:
            pass

    # DISCOUNT CALCULATION
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

    return render(request, "customer/shop.html", {
        "products": page_obj,   # ✅ IMPORTANT FIX
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
    return render(request, "customer/search.html", {"results": results})


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

    return render(request, "customer/cart.html", {
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
    cart_count = sum(cart.values())
    return JsonResponse({
        "success": True,
        "cart_count": cart_count
    })
    
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

def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "status": "ok",
        "cart": cart,
    })

def clear_cart(request):
    request.session["cart"] = {}
    request.session["selected_items"] = []
    request.session.modified = True

    return redirect("cart")

def clear_cart_session(request):
    request.session["cart"] = {}
    request.session.modified = True
    return redirect("cart")

@require_POST
def update_selected_items(request):
    import json
    from decimal import Decimal

    data = json.loads(request.body)
    selected = set(str(i) for i in data.get("selected", []))

    request.session["selected_items"] = list(selected)
    request.session.modified = True

    cart = {str(k): v for k, v in request.session.get("cart", {}).items()}

    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")

    for pid, qty in cart.items():
        if pid not in selected:
            continue

        product = Product.objects.get(id=pid)
        qty = int(qty)

        final_price, _, _ = calculate_discounted_price(product)
        final_price = Decimal(str(final_price))
        selling_price = Decimal(str(product.selling_price or 0))

        subtotal += selling_price * qty
        discount_total += (selling_price - final_price) * qty

    total = subtotal - discount_total

    return JsonResponse({
        "subtotal": float(subtotal),
        "discount_total": float(discount_total),
        "total": float(total),
        "selected_count": len(selected)
    })

def checkout_view(request):
    import uuid

    # ✅ GET OR CREATE GUEST ID (PERSISTENT)
    guest_id = request.COOKIES.get('guest_id')
    if not guest_id:
        guest_id = str(uuid.uuid4())

    cart = request.session.get("cart", {})
    selected_keys = request.session.get("selected_items", list(cart.keys()))
    selected_keys = [str(x) for x in selected_keys]

    cart_items = []
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")
    final_total = Decimal("0.00")   

    customer = None
    customer_id = request.session.get("customer_id")

    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()

    for pid, qty in cart.items():
        pid = str(pid)

        if pid not in selected_keys:
            continue

        product = get_object_or_404(Product, id=pid)
        qty = int(qty)

        final_price, _, _ = calculate_discounted_price(product)
        final_price = Decimal(str(final_price or 0))

        selling_price = Decimal(str(product.selling_price or 0))

        line_original = selling_price * qty
        line_final = final_price * qty
        line_discount = line_original - line_final

        subtotal += line_original
        discount_total += line_discount
        final_total += line_final

        cart_items.append({
            "product": product,
            "qty": qty,
            "original_price": selling_price,
            "price": final_price,
            "line_original": line_original,
            "line_final": line_final,
            "discount_amount": line_discount,
        })

    payment_choices = [
        ("COD", "Cash on Delivery"),
        ("GCASH", "GCash"),
    ]

    response = render(request, "customer/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount_total": discount_total,
        "total_amount": final_total,
        "payment_choices": payment_choices,
        "customer": customer,
    })

    # ✅ SAVE COOKIE (VERY IMPORTANT)
    response.set_cookie('guest_id', guest_id, max_age=60*60*24*30)

    return response

@transaction.atomic
def process_sale(request):
    import uuid

    if request.method != "POST":
        return redirect("checkout")

    # ✅ GET OR CREATE GUEST ID
    guest_id = request.COOKIES.get("guest_id")
    if not guest_id:
        guest_id = str(uuid.uuid4())

    cart = request.session.get("cart", {})
    selected_keys = request.session.get("selected_items", list(cart.keys()))

    full_name = request.POST.get("full_name") or "Walk-in Customer"
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    payment_method = request.POST.get("payment_method")

    customer = None

    # ===== EXISTING CUSTOMER LOGIC (UNCHANGED) =====
    if phone:
        customer, created = Customer.objects.get_or_create(
            phone=phone,
            defaults={
                "full_name": full_name,
                "email": email
            }
        )

        if not created:
            updated = False

            if full_name and customer.full_name != full_name:
                customer.full_name = full_name
                updated = True

            if email and customer.email != email:
                customer.email = email
                updated = True

            if updated:
                customer.save()

    else:
        customer_id = request.session.get("customer_id")

        if customer_id:
            customer = Customer.objects.filter(id=customer_id).first()

        if not customer:
            customer = Customer.objects.create(
                full_name=full_name,
                email=email
            )

    request.session["customer_id"] = customer.id

    # ✅ SAVE SALE WITH guest_id
    sale = Sale.objects.create(
        customer=customer,
        guest_id=guest_id,   # 🔥 THIS IS THE FIX
        payment_method=payment_method,
        status="pending"
    )

    subtotal = 0
    discount_total = 0

    for pid, qty in cart.items():

        if pid not in selected_keys:
            continue

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

        product.stock_qty = max((product.stock_qty or 0) - qty, 0)
        product.save()

    sale.subtotal = subtotal
    sale.total_amount = subtotal - discount_total
    sale.save()

    request.session["cart"] = {}
    request.session["selected_items"] = []
    request.session["last_order_code"] = str(sale.order_code)

    messages.success(request, "Order placed successfully!")

    response = redirect("dashboard")

    # ✅ SAVE COOKIE (PERSISTENT 30 DAYS)
    response.set_cookie("guest_id", guest_id, max_age=60*60*24*30)

    return response

def orders_view(request):
    customer = None
    orders = []

    # ✅ PRIORITY 1: session customer (if still exists)
    customer_id = request.session.get("customer_id")
    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()

    # ✅ PRIORITY 2: cookie-based guest tracking
    guest_id = request.COOKIES.get("guest_id")

    # ✅ PRIORITY 3: manual lookup (phone/email)
    if not customer:
        phone = request.GET.get("phone")
        email = request.GET.get("email")

        if phone:
            customer = Customer.objects.filter(phone=phone).first()
        elif email:
            customer = Customer.objects.filter(email=email).first()

        if customer:
            request.session["customer_id"] = customer.id

    # ===== FETCH ORDERS =====
    if customer:
        orders = Sale.objects.filter(customer=customer).order_by("-sale_date")

    elif guest_id:
        orders = Sale.objects.filter(guest_id=guest_id).order_by("-sale_date")

    return render(request, "customer/orders/orders.html", {
        "orders": orders,
        "customer": customer,
    })

def order_detail(request, order_code):
    phone = request.GET.get("phone")
    order = get_object_or_404(Sale, order_code=order_code)


    if not phone:
        return redirect("order_history")  # prevent broken access

    order = get_object_or_404(
        Sale,
        id=sale_id,
        customer__phone=phone
    )

    return render(request, "customer/orders/order_detail.html", {
        "order": order,
        "phone": phone  # 👈 keep this!
    })

@require_POST
def cancel_order(request, order_code):
    sale = get_object_or_404(Sale, order_code=order_code)

    if not sale.can_cancel():
        return JsonResponse({'error': 'Cannot cancel this order'}, status=400)

    sale.status = 'cancelled'
    sale.save()

    return JsonResponse({'success': True})

def track_order(request, order_code):

    sale = get_object_or_404(Sale, order_code=order_code)
    items = sale.sale_items.all()

    # Timeline steps
    steps = [
        "pending",
        "processing",
        "shipped",
        "completed",
        "cancelled"
    ]

    status = (sale.status or "pending").lower()

    current_index = 0
    if status == "cancelled":
        current_index = len(steps) - 1
    elif status == "completed":
        current_index = 3
    elif status == "shipped":
        current_index = 2
    elif status == "processing":
        current_index = 1
    elif status == "pending":
        current_index = 0


    can_cancel = (
        status in ["pending", "processing"] and
        timezone.now() <= sale.sale_date + timedelta(hours=24)
    )

    progress_percent = 0
    if len(steps) > 1:
        progress_percent = (current_index / (len(steps) - 1)) * 100

    context = {
        "sale": sale,
        "items": items,
        "steps": steps,
        "current_index": current_index,
        "status": status,
        "can_cancel": can_cancel,  # 👈 IMPORTANT
        "progress_percent": progress_percent,
    }

    return render(request, "customer/orders/track_order.html", context)
    
def buy_again(request, order_code):

    sale = get_object_or_404(Sale, order_code=order_code)

    cart = {}
    selected_items = []

    for item in sale.sale_items.all():
        pid = str(item.product.id)

        cart[pid] = item.quantity
        selected_items.append(pid)

    # IMPORTANT: sync BOTH
    request.session["cart"] = cart
    request.session["selected_items"] = selected_items

    request.session.modified = True

    return redirect("checkout")

def help_center(request):

    help_data = HelpCenter.objects.first()

    return render(request, "customer/help_page.html", {
        "help": help_data
    })

def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            obj, created = NewsletterSubscriber.objects.get_or_create(email=email)

            if created:
                messages.success(request, "Subscribed successfully!")
            else:
                messages.info(request, "You are already subscribed.")

    return redirect(request.META.get("HTTP_REFERER", "/"))