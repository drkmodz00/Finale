# from decimal import Decimal
# from django.shortcuts import render, get_object_or_404, redirect
# from django.db import transaction
# from django.contrib import messages
# from django.db.models import Sum, Count, F
# from django.utils import timezone
# from datetime import date

# from ..models import Product, Sale, SaleItem, Customer, Cashier
# from ..utils.discounts import calculate_discounted_price


# # =========================
# # AUTH HELPERS (SESSION-BASED)
# # =========================

# def cashier_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not request.session.get("user_id"):
#             return redirect("login")

#         if request.session.get("role") != "cashier":
#             return redirect("admin_dashboard")

#         return view_func(request, *args, **kwargs)
#     return wrapper


# def admin_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not request.session.get("user_id"):
#             return redirect("login")

#         if request.session.get("role") != "admin":
#             return redirect("cashier_dashboard")

#         return view_func(request, *args, **kwargs)
#     return wrapper


# # =========================
# # AUTH VIEWS
# # =========================

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         try:
#             user = Cashier.objects.get(username=username)

#             try:
#                 valid = user.check_password(password)
#             except Exception:
#                 valid = False

#             if not valid:
#                 messages.error(request, "Invalid credentials")
#                 return redirect("login")

#             if user.status != "active":
#                 messages.error(request, "Account is inactive.")
#                 return redirect("login")

#             # Save session
#             request.session["user_id"] = user.id
#             request.session["username"] = user.username
#             request.session["role"] = user.role

#             # ✅ ROLE-BASED REDIRECTION
#             if user.role == "admin":
#                 return redirect("admin_dashboard")
#             elif user.role == "cashier":
#                 return redirect("pos_dashboard")
#             else:
#                 return redirect("login")

#         except Cashier.DoesNotExist:
#             messages.error(request, "User not found")
#             return redirect("login")

#     return render(request, "registration/login.html")


# def logout_view(request):
#     request.session.flush()
#     return redirect("login")


# # =========================
# # DASHBOARDS
# # =========================

# @cashier_required
# def pos_dashboard(request):
#     today = timezone.now().date()

#     # SESSION CART (safe)
#     cart = request.session.get("cart", {})
#     cart_count = sum(cart.values()) if cart else 0

#     # PRODUCTS
#     product_count = Product.objects.count()

#     # TODAY SALES
#     today_sales = Sale.objects.filter(
#         sale_date__date=today
#     )

#     total_sales = today_sales.aggregate(
#         total=Sum("total_amount")
#     )["total"] or 0

#     transaction_count = today_sales.count()

#     # TOTAL REVENUE (ALL TIME)
#     total_revenue = Sale.objects.aggregate(
#         total=Sum("total_amount")
#     )["total"] or 0

#     # LOW STOCK ALERT
#     low_stock = Product.objects.filter(
#         stock_qty__lte=F("reorder_level")
#     ).count()

#     context = {
#         "cart_count": cart_count,
#         "product_count": product_count,
#         "total_sales": total_sales,
#         "transaction_count": transaction_count,
#         "total_revenue": total_revenue,
#         "low_stock": low_stock,
#     }

#     return render(request, "cashier/dashboard.html", context)

# @cashier_required
# def pos_sell(request):
#     products = Product.objects.all()

#     cart = request.session.get("cart", {})
#     cart_items = []
#     total = 0

#     for pid, qty in cart.items():
#         product = Product.objects.get(id=pid)
#         price, _, _ = calculate_discounted_price(product)

#         subtotal = price * qty
#         total += subtotal

#         cart_items.append({
#             "product": product,
#             "qty": qty,
#             "subtotal": subtotal
#         })

#     return render(request, "cashier/sell.html", {
#         "products": products,
#         "cart_items": cart_items,
#         "total": total
#     })
# # =========================
# # CART VIEW
# # =========================

# @cashier_required
# def cart_view(request):
#     cart = request.session.get("cart", {})
#     items = []
#     total = 0

#     for pid, qty in cart.items():
#         product = get_object_or_404(Product, id=pid)
#         qty = int(qty)

#         price, _, _ = calculate_discounted_price(product)
#         total += price * qty

#         items.append({
#             "product": product,
#             "qty": qty,
#             "price": price
#         })

#     return render(request, "cashier/cart.html", {
#         "items": items,
#         "total": total
#     })

# @cashier_required
# def add_to_cart(request, pid):
#     cart = request.session.get("cart", {})

#     pid = str(pid)
#     cart[pid] = cart.get(pid, 0) + 1

#     request.session["cart"] = cart
#     request.session.modified = True

#     return redirect("pos_dashboard")

# @cashier_required
# def update_cart(request, pid):
#     if request.method == "POST":
#         qty = int(request.POST.get("qty", 1))

#         cart = request.session.get("cart", {})
#         pid = str(pid)

#         if qty <= 0:
#             cart.pop(pid, None)
#         else:
#             cart[pid] = qty

#         request.session["cart"] = cart
#         request.session.modified = True

#     return redirect("pos_dashboard")

# @cashier_required
# def remove_from_cart(request, pid):
#     cart = request.session.get("cart", {})
#     cart.pop(str(pid), None)

#     request.session["cart"] = cart
#     request.session.modified = True

#     return redirect("pos_dashboard")
# # =========================
# # CHECKOUT VIEW
# # =========================

# @cashier_required
# def checkout_view(request):
#     cart = request.session.get("cart", {})
#     selected_keys = request.session.get("selected_items", list(cart.keys()))

#     if not cart:
#         messages.error(request, "Cart is empty.")
#         return redirect("pos_cart")

#     cart_items = []
#     subtotal = Decimal("0.00")
#     discount_total = Decimal("0.00")

#     for pid, qty in cart.items():
#         if pid not in selected_keys:
#             continue

#         product = get_object_or_404(Product, id=pid)
#         qty = int(qty)

#         final_price, _, _ = calculate_discounted_price(product)
#         final_price = Decimal(final_price)

#         selling_price = Decimal(product.selling_price or 0)

#         line_original = selling_price * qty
#         line_final = final_price * qty
#         line_discount = line_original - line_final

#         subtotal += line_original
#         discount_total += line_discount

#         cart_items.append({
#             "product": product,
#             "qty": qty,
#             "price": final_price,
#             "discount_amount": line_discount,
#         })

#     payment_choices = [
#         ("gcash", "GCash"),
#         ("cod", "Cash on Delivery"),
#     ]

#     return render(request, "cashier/checkout.html", {
#         "cart_items": cart_items,
#         "subtotal": subtotal,
#         "discount_total": discount_total,
#         "total_amount": subtotal - discount_total,
#         "payment_choices": payment_choices,
#     })


# # =========================
# # PROCESS SALE
# # =========================

# @transaction.atomic
# @cashier_required
# def process_sale(request):
#     if request.method != "POST":
#         return redirect("checkout")

#     cart = request.session.get("cart", {})

#     if not cart:
#         messages.error(request, "Cart is empty.")
#         return redirect("pos_sell")

#     cashier = Cashier.objects.get(id=request.session["user_id"])

#     payment_method = request.POST.get("payment_method", "cash")
#     cash_received = float(request.POST.get("cash", 0))

#     subtotal = 0
#     sale_items_data = []

#     # CREATE SALE FIRST
#     sale = Sale.objects.create(
#         cashier=cashier,
#         payment_method=payment_method,
#         amount_tendered=cash_received,
#         status="completed"
#     )

#     # PROCESS ITEMS
#     for pid, qty in cart.items():
#         product = get_object_or_404(Product, id=pid)
#         qty = int(qty)

#         price, _, _ = calculate_discounted_price(product)

#         line_total = price * qty
#         subtotal += line_total

#         # STOCK DEDUCTION
#         product.stock_qty -= qty
#         product.save()

#         SaleItem.objects.create(
#             sale=sale,
#             product=product,
#             quantity=qty,
#             unit_price=price,
#             line_total=line_total
#         )

#     # FINAL CALCULATIONS
#     tax = subtotal * 0.12  # optional VAT example
#     total = subtotal + tax
#     change = cash_received - total

#     sale.subtotal = subtotal
#     sale.tax_amount = tax
#     sale.total_amount = total
#     sale.change_given = change
#     sale.save()

#     # CLEAR CART
#     request.session["cart"] = {}
#     request.session.modified = True

#     messages.success(request, f"Sale completed! Change: ₱{change:.2f}")
#     return redirect("pos_sell")