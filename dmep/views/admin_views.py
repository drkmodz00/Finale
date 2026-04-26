from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q, Count, Avg
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from ..models import *
from dmep.utils.discounts import calculate_discounted_price


def is_admin(user):
    return user.groups.filter(name='admin').exists()
# # =========================================================
# # ADMIN CHECK
# # =========================================================
# def admin_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not request.session.get("user_id"):
#             return redirect("login")

#         if request.session.get("role") != "admin":
#             return redirect("cashier_dashboard")

#         return view_func(request, *args, **kwargs)
#     return wrapper


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile, created = Profile.objects.get_or_create(user=user)
            # Superuser
            if user.is_superuser:
                return redirect('admin_dashboard')

            # Staff/Admin Role
            elif hasattr(user, 'profile') and user.profile.role == 'admin':
                return redirect('admin_dashboard')

            else:
                return redirect('login')

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'registration/login.html')
    
def logout_view(request):
    logout(request)
    return redirect("login")
    
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # 👈 new field

        # check duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        # create user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # assign role (group)
        # if role in ["admin", "cashier", "manager"]:
        if role in ["admin"]:

            group = Group.objects.get(name=role)
            user.groups.add(group)
        else:
            messages.error(request, "Invalid role selected")
            return redirect("signup")

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "registration/signup.html")
    
    # =========================================================
# DASHBOARD
# =========================================================
@login_required
@user_passes_test(is_admin)
def dashboard(request):

    context = {
        "product_count": Product.objects.count(),
        "customer_count": Customer.objects.count(),
        "supplier_count": Supplier.objects.count(),
        "sale_count": Sale.objects.count(),

        "total_sales": Sale.objects.filter(status="delivered").aggregate(
            total=Sum("total_amount")
        )["total"] or 0,

        "low_stock": Product.objects.filter(stock_qty__lte=10).count(),

        # ✅ FIXED ordering
        "latest_products": Product.objects.order_by("-id")[:5],
        "latest_sales": Sale.objects.order_by("-sale_date")[:5],

        # ✅ NOW USE REAL TIMESTAMP FIELD
        "latest_customers": Customer.objects.order_by("-created_at")[:5],
    }

    return render(request, "panel/dashboard.html", context)

# =========================================================
# SUPPLIERS (READ ONLY)
# =========================================================

@login_required
@user_passes_test(is_admin)
def supplier_list(request):

    if request.method == "POST":

        action = request.POST.get("action")

        # CREATE
        if action == "create":
            Supplier.objects.create(
                name=request.POST.get("name"),
                contact_person=request.POST.get("contact_person"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email"),
                address=request.POST.get("address"),
            )
            messages.success(request, "Supplier created successfully")

        # UPDATE
        elif action == "update":
            supplier = get_object_or_404(Supplier, id=request.POST.get("id"))

            supplier.name = request.POST.get("name")
            supplier.contact_person = request.POST.get("contact_person")
            supplier.phone = request.POST.get("phone")
            supplier.email = request.POST.get("email")
            supplier.address = request.POST.get("address")
            supplier.save()

            messages.success(request, "Supplier updated successfully")

        # DELETE
        elif action == "delete":
            supplier = get_object_or_404(Supplier, id=request.POST.get("id"))
            supplier.delete()

            messages.success(request, "Supplier deleted successfully")

        return redirect("supplier_list")

    suppliers = Supplier.objects.all()

    return render(request, "panel/suppliers.html", {
        "suppliers": suppliers
    })
    
    # =========================================================
# CUSTOMERS (READ ONLY)
# =========================================================
@login_required
@user_passes_test(is_admin)
def customer_list(request):

    customers = Customer.objects.all().annotate(
        sale_count=Count("sales")
    )

    # SEARCH
    q = request.GET.get("q")
    if q:
        customers = customers.filter(
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    # SORT
    sort = request.GET.get("sort")
    if sort == "sales":
        customers = customers.order_by("-sale_count")
    elif sort == "name":
        customers = customers.order_by("full_name")
    else:
        customers = customers.order_by("-loyalty_points")

    # progress %
    for c in customers:
        c.pts_percent = min((c.loyalty_points / 1000) * 100, 100)

    paginator = Paginator(customers, 20)
    page = request.GET.get("page")
    customers = paginator.get_page(page)

    return render(request, "panel/customers.html", {
        "customers": customers
    })

@login_required
@user_passes_test(is_admin)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    sales = (
        customer.sales
        .exclude(status__in=["cancelled", "refunded"])
        .prefetch_related("sale_items__product__category", "tracking")
        .order_by("-sale_date")
    )

    total_spent = sales.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    for sale in sales:
        sale.total_savings = sum(
            item.discount_amount or 0
            for item in sale.sale_items.all()
        )
    return render(request, "panel/customer_details.html", {
        "customer": customer,
        "sales": sales,
        "total_spent": total_spent,
    })           
    
             # =========================================================
# PRODUCTS (LIST ONLY TEMPLATE + URL CRUD)
# =========================================================
@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    active_products = Product.objects.filter(status='active').count()
    low_stock = Product.objects.filter(
        stock_qty__lte=models.F('reorder_level'),
        stock_qty__isnull=False,
        reorder_level__isnull=False
    ).count()

    return render(request, "panel/product.html", {
        "products": products,
        "categories": categories,
        "suppliers": suppliers,
        "active_products": active_products,
        "low_stock": low_stock,
    })

@login_required
@user_passes_test(is_admin)
def product_upsert(request):
    if request.method == "POST":

        product_id = request.POST.get("product_id")

        category_id = request.POST.get("category")
        supplier_id = request.POST.get("supplier")

        # -----------------------------
        # GET OR CREATE PRODUCT
        # -----------------------------
        if product_id:
            product = get_object_or_404(Product, id=product_id)
        else:
            product = Product()

        # -----------------------------
        # BASIC FIELDS
        # -----------------------------
        product.name = request.POST.get("name")
        product.sku = request.POST.get("sku")
        product.barcode = request.POST.get("barcode")
        product.unit = request.POST.get("unit")
        product.status = request.POST.get("status") or "active"

        # -----------------------------
        # NUMBERS (SAFE CONVERSION)
        # -----------------------------
        product.cost_price = request.POST.get("cost_price") or None
        product.selling_price = request.POST.get("selling_price") or None
        product.stock_qty = request.POST.get("stock_qty") or None
        product.reorder_level = request.POST.get("reorder_level") or None

        # -----------------------------
        # CATEGORY
        # -----------------------------
        product.category = (
            get_object_or_404(Category, id=category_id)
            if category_id else None
        )

        # -----------------------------
        # SUPPLIER
        # -----------------------------
        product.supplier = (
            get_object_or_404(Supplier, id=supplier_id)
            if supplier_id else None
        )

        # -----------------------------
        # IMAGE (ONLY IF NEW FILE UPLOADED)
        # -----------------------------
        if "image" in request.FILES:
            file = request.FILES["image"]
            image_url = upload_to_supabase(file)
            product.image_url = image_url

        # -----------------------------
        # SAVE (CREATE OR UPDATE)
        # -----------------------------
        product.save()

        if product_id:
            messages.success(request, "Product updated successfully")
        else:
            messages.success(request, "Product created successfully")

    return redirect("product_list")


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted")

    return redirect("product_list")


# =========================================================
# SALES (LIST ONLY)
# =========================================================
# @login_required
# @user_passes_test(is_admin)
# def sale_list(request):
#     return render(request, "panel/sales.html", {
#         "sales": Sale.objects.select_related("customer").all()
#     })

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def sale_create(request):

    if request.method != "POST":
        return redirect("sale_list")

    customer_id = request.POST.get("customer_id")

    sale = Sale.objects.create(
        customer_id=customer_id,
        status="pending",
        subtotal=0,
        total_amount=0
    )

    product_ids = request.POST.getlist("product_id")
    quantities = request.POST.getlist("quantity")

    subtotal = 0
    total = 0

    for product_id, qty in zip(product_ids, quantities):

        if not product_id or not qty:
            continue

        product = Product.objects.select_for_update().filter(id=product_id).first()
        if not product:
            continue

        qty = int(qty)

        if qty <= 0:
            continue

        if product.stock_qty is None:
            continue

        if product.stock_qty < qty:
            continue

        # =========================
        # ORIGINAL PRICE
        # =========================
        original_price = float(product.selling_price or 0)

        # =========================
        # DISCOUNT ENGINE (FIXED IMPORT)
        # =========================
        final_price, discount_obj, discount_pct = calculate_discounted_price(product)

        if final_price is None:
            final_price = original_price
            discount_obj = None
            discount_pct = 0

        # =========================
        # CALCULATION
        # =========================
        line_total = final_price * qty
        discount_amount = (original_price - final_price) * qty

        subtotal += original_price * qty
        total += line_total

        # =========================
        # STOCK UPDATE
        # =========================
        product.stock_qty -= qty
        product.save()

        # =========================
        # SAVE ITEM
        # =========================
        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=qty,
            unit_price=original_price,
            line_total=line_total,

            discount_name=discount_obj.name if discount_obj else None,
            discount_type=getattr(discount_obj, "type", None),
            discount_pct=float(discount_pct or 0),
            discount_amount=float(discount_amount or 0)
        )

    # =========================
    # FINAL TOTALS
    # =========================
    sale.subtotal = round(subtotal, 2)
    sale.total_amount = round(total, 2)
    sale.save()

    OrderTracking.objects.create(
        sale=sale,
        status="processing",
        note="Order created"
    )

    return redirect("sale_list")
    
@login_required
@user_passes_test(is_admin)
def sale_list(request):

    sales_qs = Sale.objects.all().prefetch_related(
        "customer",
        "sale_items__product__category"
    ).order_by("-sale_date")

    # SEARCH
    q = request.GET.get("q")
    if q:
        sales_qs = sales_qs.filter(
            Q(customer__full_name__icontains=q) |
            Q(customer__email__icontains=q) |
            Q(customer__phone__icontains=q) |
            Q(id__icontains=q)
        )

    # FILTER
    status = request.GET.get("status")
    if status:
        sales_qs = sales_qs.filter(status=status)

    # =========================
    # STATS
    # =========================
    total_sales = sales_qs.aggregate(total=Sum("total_amount"))["total"] or 0
    total_orders = sales_qs.count()
    avg_order = sales_qs.aggregate(avg=Avg("total_amount"))["avg"] or 0

    today = date.today()
    today_sales = sales_qs.filter(
        sale_date__date=today
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    pending_orders = sales_qs.filter(status="pending").count()
    cancelled_orders = sales_qs.filter(status="cancelled").count()

    # Top product (simple version)
    top_product = None
    from django.db.models import F

    top_item = SaleItem.objects.values(
        "product__name"
    ).annotate(
        total_qty=Sum("quantity")
    ).order_by("-total_qty").first()

    if top_item:
        top_product = top_item["product__name"]

    # PAGINATION
    paginator = Paginator(sales_qs, 20)
    page = request.GET.get("page")
    sales = paginator.get_page(page)

    return render(request, "panel/sales.html", {
        "sales": sales,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "avg_order": avg_order,
        "today_sales": today_sales,
        "pending_orders": pending_orders,
        "cancelled_orders": cancelled_orders,
        "top_product": top_product,
    })

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def sale_void(request, pk):
    sale = get_object_or_404(Sale, pk=pk)

    if request.method == "POST":

        if sale.status == "cancelled":
            messages.info(request, f"Sale #{sale.id} is already cancelled")
            return redirect("sale_list")

        # restore stock
        for item in sale.sale_items.select_related("product").all():
            if item.product:
                item.product.stock_qty += item.quantity
                item.product.save()

        sale.status = "cancelled"
        sale.save()

        messages.warning(request, f"Sale #{sale.id} has been voided")

    return redirect("sale_list")

@login_required
@user_passes_test(is_admin)
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale.delete()
    messages.success(request, f"Sale #{sale.id} has been deleted")
    return redirect("sale_list")
# =========================================================
# PURCHASE ORDER
# =========================================================
@login_required
@user_passes_test(is_admin)
def po_list(request):
    return render(request, "panel/purchase_orders.html", {
        "pos": PurchaseOrder.objects.select_related("supplier")
    })

@login_required
@user_passes_test(is_admin)
def po_create(request):
    if request.method == "POST":
        PurchaseOrder.objects.create(
            supplier_id=request.POST.get("supplier"),
            status="pending"
        )
        messages.success(request, "PO created")

    return redirect("po_list")

@login_required
@user_passes_test(is_admin)
def po_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == "POST":

        for item in po.po_items.all():
            qty = int(request.POST.get(f"qty_{item.id}", 0))

            item.qty_received = qty
            item.save()

            if item.product:
                item.product.stock_qty = (item.product.stock_qty or 0) + qty
                item.product.save()

        po.status = "received"
        po.received_date = timezone.now()
        po.save()

        messages.success(request, f"PO #{po.id} received")

    return redirect("po_list")


# =========================================================
# STOCK MOVEMENTS
# =========================================================
@login_required
@user_passes_test(is_admin)
def stock_movement_list(request):
    return render(request, "panel/stock.html", {
        "movements": StockMovement.objects.select_related("product")
    })


# =========================================================
# DISCOUNTS (YOUR STANDARD STYLE)
# =========================================================
# @login_required
# @user_passes_test(is_admin)
# def get_applicable_discount(product):
#     today = timezone.now().date()

#     discounts = Discount.objects.filter(status="active").filter(
#         # FIX: allow NULL dates
#         Q(valid_from__isnull=True) | Q(valid_from__lte=today),
#         Q(valid_until__isnull=True) | Q(valid_until__gte=today)
#     )

#     best_discount = None
#     best_value = 0

#     product_category_id = product.category_id
#     product_id = product.id

#     for d in discounts:

#         value = 0

#         # ALL PRODUCTS
#         if d.applies_to == "all":
#             value = d.value or 0

#         # CATEGORY
#         elif d.applies_to == "category":
#             if not d.categories.filter(id=product_category_id).exists():
#                 continue
#             value = d.value or 0

#         # PRODUCT
#         elif d.applies_to == "product":
#             if not d.products.filter(id=product_id).exists():
#                 continue
#             value = d.value or 0

#         else:
#             continue

#         if value > best_value:
#             best_value = value
#             best_discount = d

#     return best_discount    
@login_required
@user_passes_test(is_admin)
def discounts(request):

    # =========================
    # AUTO EXPIRE DISCOUNTS
    # =========================
    today = timezone.now().date()
    Discount.objects.filter(valid_until__lt=today).update(status="expired")

    # =========================
    # POST HANDLER
    # =========================
    if request.method == "POST":
        action = request.POST.get("action")

        # =========================
        # CREATE
        # =========================
        if action == "create":

            discount = Discount.objects.create(
                name=request.POST.get("name"),
                type=request.POST.get("type"),
                value=request.POST.get("value") or 0,
                applies_to=request.POST.get("applies_to"),
                status=request.POST.get("status") or "active",
            )

            # -------------------------
            # CATEGORY (FIXED)
            # -------------------------
            category_id = request.POST.get("category")
            if category_id:
                discount.categories.add(category_id)

            # -------------------------
            # PRODUCTS (MANY)
            # -------------------------
            product_ids = request.POST.getlist("products")
            if product_ids:
                discount.products.set(product_ids)

            messages.success(request, "Discount created successfully")

        # =========================
        # UPDATE
        # =========================
        elif action == "update":

            d = get_object_or_404(Discount, id=request.POST.get("id"))

            d.name = request.POST.get("name")
            d.type = request.POST.get("type")
            d.value = request.POST.get("value") or 0
            d.applies_to = request.POST.get("applies_to")
            d.status = request.POST.get("status")
            d.save()

            # -------------------------
            # CATEGORY UPDATE (FIXED)
            # -------------------------
            category_id = request.POST.get("category")

            if category_id:
                d.categories.set([category_id])
            else:
                d.categories.clear()

            # -------------------------
            # PRODUCTS UPDATE
            # -------------------------
            product_ids = request.POST.getlist("products")

            if product_ids:
                d.products.set(product_ids)
            else:
                d.products.clear()

            messages.success(request, "Discount updated successfully")

        # =========================
        # DELETE
        # =========================
        elif action == "delete":
            Discount.objects.filter(id=request.POST.get("id")).delete()
            messages.success(request, "Discount deleted successfully")

        return redirect("discounts")

    # =========================
    # QUERY DATA
    # =========================
    discounts = Discount.objects.all().order_by("-id")

    categories = Category.objects.all()
    products = Product.objects.all()

    # =========================
    # CONTEXT
    # =========================
    return render(request, "panel/discounts.html", {
        "discounts": discounts,
        "categories": categories,
        "products": products,
        "active_count": discounts.filter(status="active").count(),
        "expired_count": discounts.filter(status="expired").count(),
    })
    
@login_required
@user_passes_test(is_admin)
def category_list(request):

    if request.method == "POST":
        action = request.POST.get("action")

        name = request.POST.get("name")
        description = request.POST.get("description")
        parent_id = request.POST.get("parent")
        img = request.FILES.get("img")

        parent = None
        if parent_id:
            parent = Category.objects.filter(id=parent_id).first()

        # CREATE
        if action == "create":
            Category.objects.create(
                name=name,
                description=description,
                parent=parent,
                img=img
            )
            messages.success(request, "Category created successfully")

        # UPDATE
        elif action == "update":
            category = get_object_or_404(Category, id=request.POST.get("id"))

            # جلوگیری از اینکه خودش والد خودش شود
            if parent and str(category.id) == parent_id:
                messages.error(request, "Category cannot be its own parent")
                return redirect("category_list")

            category.name = name
            category.description = description
            category.parent = parent

            if img:
                category.img = img

            category.save()
            messages.success(request, "Category updated successfully")

        # DELETE
        elif action == "delete":
            category = get_object_or_404(Category, id=request.POST.get("id"))
            category.delete()
            messages.success(request, "Category deleted successfully")

        return redirect("category_list")

    categories = Category.objects.all().select_related("parent").prefetch_related("subcategories", "products")

    categories_with_products = sum(1 for c in categories if c.products.exists())
    empty_categories = sum(1 for c in categories if not c.products.exists())

    return render(request, "panel/categories.html", {
        "categories": categories,
        "categories_with_products": categories_with_products,
        "empty_categories": empty_categories,
    })