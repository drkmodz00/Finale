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
from dmep.utils.po import recalc_po_total
from cloudinary.uploader import upload


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
    
def create_po_with_items(supplier_id, items):

    with transaction.atomic():

        po = PurchaseOrder.objects.create(
            supplier_id=supplier_id,
            status="pending"
        )

        total_cost = 0

        for item in items:

            product_id = item.get("id")
            qty = int(item.get("qty", 0))
            cost = float(item.get("cost", 0))

            if qty <= 0:
                continue

            POItem.objects.create(
                po=po,
                product_id=product_id,
                qty_ordered=qty,
                unit_cost=cost
            )

            total_cost += qty * cost

        po.total_cost = total_cost
        po.save()

    return po

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

        #         unit_cost=cost
        #     )

        #     po.total_cost = (po.total_cost or 0) + (qty * cost)
        #     po.save()

        # return JsonResponse({"success": True})
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
            Q(address__icontains=q) |
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
    
@login_required
@user_passes_test(is_admin)
def supplier_pos(request, supplier_id):

    supplier = get_object_or_404(Supplier, id=supplier_id)

    suppliers = Supplier.objects.all()   # ✅ ADD THIS

    products = Product.objects.filter(
        supplier_id=supplier_id,
        status='active'
    )

    pos = PurchaseOrder.objects.filter(
        supplier_id=supplier_id
    ).prefetch_related('po_items__product')

    return render(request, "panel/po.html", {
        "supplier": supplier,
        "suppliers": suppliers,   # ✅ REQUIRED FOR DROPDOWN
        "products": products,
        "pos": pos
    })

@login_required
@user_passes_test(is_admin)
def supplier_purchase(request, supplier_id):

    if request.method == "POST":
        data = json.loads(request.body)

        product_id = data["productId"]
        qty = int(data["qty"])
        cost = float(data["cost"])

        with transaction.atomic():

            po, created =PurchaseOrder.objects.get_or_create(
                supplier_id=supplier_id,
                status="pending"
            )

            item = POItem.objects.create(
                po=po,
                product_id=product_id,
                qty_ordered=qty,
                unit_cost=cost
            )

            po.total_cost = (po.total_cost or 0) + (qty * cost)
            po.save()

        return JsonResponse({"success": True})

@login_required
@user_passes_test(is_admin)
def ajax_supplier_products(request):
    supplier_id = request.GET.get("supplier_id")

    if not supplier_id:
        return JsonResponse([], safe=False)

    products = Product.objects.filter(
        supplier_id=supplier_id
    ).values("id", "name")

    return JsonResponse(list(products), safe=False)

@login_required
@user_passes_test(is_admin)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    sales = (
        customer.sales
        .exclude(status__in=["cancelled", "refunded"])
        .prefetch_related("sale_items__product__category")
        .order_by("-sale_date")
    )

    total_spent = sales.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    # ✅ compute savings per sale
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

@login_required
@user_passes_test(is_admin)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect("customer_list")
    
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

        # GET OR CREATE
        if product_id:
            product = get_object_or_404(Product, id=product_id)
        else:
            product = Product()

        # BASIC FIELDS
        product.name = request.POST.get("name")
        product.sku = request.POST.get("sku")
        product.barcode = request.POST.get("barcode")
        product.unit = request.POST.get("unit")
        product.status = request.POST.get("status") or "active"

        # ✅ NUMERIC FIELDS (SAFE CAST)
        try:
            product.cost_price = float(request.POST.get("cost_price") or 0)
        except:
            product.cost_price = 0

        try:
            product.selling_price = float(request.POST.get("selling_price") or 0)
        except:
            product.selling_price = 0

        try:
            product.stock_qty = int(request.POST.get("stock_qty") or 0)
        except:
            product.stock_qty = 0

        try:
            product.reorder_level = int(request.POST.get("reorder_level") or 0)
        except:
            product.reorder_level = 0

        # ✅ CATEGORY (SAFE)
        if category_id:
            product.category_id = category_id
        else:
            product.category = None

        # ✅ SUPPLIER (FIXED PROPERLY)
        if supplier_id:
            product.supplier_id = supplier_id
        else:
            product.supplier = None

        # ✅ IMAGE
        if "img" in request.FILES:
            result = upload(request.FILES["img"])

            product.img = result.get("public_id") 
        product.save()

        # SUCCESS MESSAGE
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
        messages.success(request, "Product deleted successfully")
        return redirect("product_list")

    return render(request, "panel/product_confirm_delete.html", {
        "product": product
    })
    
@login_required
@user_passes_test(is_admin)
@transaction.atomic
def sale_create(request):

    if request.method != "POST":
        return redirect("sale_list")

    # =========================
    # CUSTOMER DATA
    # =========================
    customer_id = request.POST.get("customer_id")
    phone = request.POST.get("phone", "")
    email = request.POST.get("email", "")
    full_name = request.POST.get("full_name", "")
    address = request.POST.get("address", "")

    # =========================
    # FIND OR CREATE CUSTOMER
    # =========================
    customer = None

    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()

    if not customer:
        if phone:
            customer = Customer.objects.filter(phone=phone).first()

        if not customer:
            customer = Customer.objects.create(
                full_name=full_name or "Guest",
                phone=phone,
                email=email,
                address=address
            )
        else:
            # Update existing
            customer.full_name = full_name or customer.full_name
            customer.email = email or customer.email
            customer.address = address or customer.address
            customer.save()

    # =========================
    # CREATE SALE
    # =========================
    sale = Sale.objects.create(
        customer=customer,
        status="pending",
        subtotal=0,
        discount_amount=0,
        total_amount=0
    )

    product_ids = request.POST.getlist("product_id")
    quantities = request.POST.getlist("quantity")

    subtotal = 0
    total = 0
    discount_total = 0  # ✅ IMPORTANT

    # =========================
    # PROCESS ITEMS
    # =========================
    for product_id, qty in zip(product_ids, quantities):

        if not product_id or not qty:
            continue

        product = Product.objects.select_for_update().filter(id=product_id).first()
        if not product:
            continue

        qty = int(qty)

        if qty <= 0:
            continue

        # STOCK CHECK
        if product.stock_qty is None or product.stock_qty < qty:
            continue

        original_price = float(product.selling_price or 0)

        # =========================
        # DISCOUNT LOGIC
        # =========================
        final_price, discount_obj, discount_pct = calculate_discounted_price(product)

        if final_price is None:
            final_price = original_price
            discount_obj = None
            discount_pct = 0

        line_total = final_price * qty
        discount_amount = (original_price - final_price) * qty

        subtotal += original_price * qty
        total += line_total
        discount_total += discount_amount  # ✅ FIX

        # =========================
        # STOCK UPDATE
        # =========================
        product.stock_qty -= qty
        product.save()

        # =========================
        # SALE ITEM
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
    # FINAL TOTALS (FIXED)
    # =========================
    sale.subtotal = round(subtotal, 2)
    sale.discount_amount = round(discount_total, 2)  # ✅ THIS FIXES YOUR ISSUE
    sale.total_amount = round(total, 2)
    sale.save()

    # =========================
    # TRACKING
    # =========================
    OrderTracking.objects.create(
        sale=sale,
        status="processing",
        note="Order created"
    )

    # =========================
    # LOYALTY POINTS
    # =========================
    points_earned = int(total // 100)
    customer.loyalty_points = (customer.loyalty_points or 0) + points_earned
    customer.save()

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

@login_required
@user_passes_test(is_admin)
def customer_by_phone(request):
    phone = request.GET.get("phone")

    customer = Customer.objects.filter(phone=phone).first()

    if not customer:
        return JsonResponse({"exists": False})

    return JsonResponse({
        "exists": True,
        "id": customer.id,
        "full_name": customer.full_name,
        "email": customer.email,
        "address": customer.address,
    })
# =========================================================
# PURCHASE ORDER
# =========================================================
# LIST
@login_required
@user_passes_test(is_admin)
def po_list(request):

    supplier_id = request.GET.get("supplier")

    pos = PurchaseOrder.objects.select_related('supplier').all().order_by('-order_date')

    if supplier_id:
        pos = pos.filter(supplier_id=supplier_id)

    suppliers = Supplier.objects.all()
    products = Product.objects.all()  # 👈 ALWAYS available (AJAX handles filtering)

    return render(request, "panel/po.html", {
        "pos": pos,
        "suppliers": suppliers,
        "products": products,
        "selected_supplier": supplier_id
    })


    # CREATE
@login_required
@user_passes_test(is_admin)
def po_create(request):

    if request.method == "POST":

        supplier_id = request.POST.get("supplier")
        product_id = request.POST.get("product")
        qty = int(request.POST.get("qty_ordered") or 0)
        cost = float(request.POST.get("unit_cost") or 0)

        if not supplier_id or not product_id or qty <= 0:
            return redirect("po_list")

        with transaction.atomic():

            po = PurchaseOrder.objects.create(
                supplier_id=supplier_id,
                status="pending"
            )

            product = Product.objects.filter(
                id=product_id,
                supplier_id=supplier_id
            ).first()

            if not product:
                return redirect("po_list")

            POItem.objects.create(
                po=po,
                product=product,
                qty_ordered=qty,
                unit_cost=cost
            )

            recalc_po_total(po)

        return redirect("po_list")

@login_required
@user_passes_test(is_admin)
def po_bulk_create(request, supplier_id):

    if request.method == "POST":

        data = json.loads(request.body)
        items = data.get("items", [])

        if not items:
            return JsonResponse({"error": "No items"}, status=400)

        with transaction.atomic():

            po = PurchaseOrder.objects.create(
                supplier_id=supplier_id,
                status="pending"
            )

            for item in items:

                qty = int(item.get("qty", 0))
                cost = float(item.get("cost", 0))
                product_id = item.get("id")

                if qty <= 0:
                    continue

                POItem.objects.create(
                    po=po,
                    product_id=product_id,
                    qty_ordered=qty,
                    unit_cost=cost
                )

            recalc_po_total(po)

        return JsonResponse({"success": True})

@login_required
@user_passes_test(is_admin)
def po_quick_purchase(request, supplier_id):

    if request.method == "POST":

        data = json.loads(request.body)

        product_id = data.get("product_id")
        qty = int(data.get("qty", 0))
        cost = float(data.get("cost", 0))

        if not product_id or qty <= 0:
            return JsonResponse({"error": "Invalid data"}, status=400)

        with transaction.atomic():

            po = PurchaseOrder.objects.create(
                supplier_id=supplier_id,
                status="pending"
            )

            POItem.objects.create(
                po=po,
                product_id=product_id,
                qty_ordered=qty,
                unit_cost=cost
            )

            recalc_po_total(po)   # ✅ FIXED (no manual math)

        return JsonResponse({"success": True})

@login_required
@user_passes_test(is_admin)
def po_receive(request, po_id):

    po = get_object_or_404(PurchaseOrder, id=po_id)

    with transaction.atomic():

        po.status = "received"
        po.received_date = timezone.now()
        po.save()

        for item in po.po_items.all():

            StockMovement.objects.create(
                product=item.product,
                type="in",
                quantity=item.qty_ordered,
                po_item=item,
                reason=f"PO #{po.id} Received"
            )

    return redirect("po_list")

@login_required
@user_passes_test(is_admin)
def po_update(request, po_id):

    po = get_object_or_404(PurchaseOrder, id=po_id)

    if request.method == "POST":
        po.supplier_id = request.POST.get("supplier")
        po.status = request.POST.get("status")
        po.save()

    return redirect("po_list")
@login_required
@user_passes_test(is_admin)
def po_delete(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)
    po.delete()

    return redirect("po_list")

@login_required
@user_passes_test(is_admin)
def po_items(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)
    products = Product.objects.all()

    return render(request, "panel/po_items.html", {
        "po": po,
        "products": products
    })

@login_required
@user_passes_test(is_admin)
def po_item_add(request, po_id):

    if request.method == "POST":

        qty = int(request.POST.get("qty_ordered") or 0)
        cost = float(request.POST.get("unit_cost") or 0)

        if qty <= 0:
            return redirect("po_items", po_id=po_id)

        POItem.objects.create(
            po_id=po_id,
            product_id=request.POST.get("product"),
            qty_ordered=qty,
            unit_cost=cost
        )

        # ✅ recalc total
        recalc_po_total(po)

    return redirect("po_items", po_id=po_id)

@login_required
@user_passes_test(is_admin)
def po_item_update(request, pk):

    item = get_object_or_404(POItem, pk=pk)
    if request.method == "POST":

        po = item.po

        item.qty_ordered = int(request.POST.get("qty_ordered") or 0)
        item.qty_received = int(request.POST.get("qty_received") or 0)
        item.unit_cost = float(request.POST.get("unit_cost") or 0)

        item.save()
        recalc_po_total(po)

    return redirect("po_items", po_id=item.po.id)

@login_required
@user_passes_test(is_admin)
def po_item_delete(request, pk):

    item = get_object_or_404(POItem, pk=pk)
    po = item.po

    if request.method == "POST":
        item.delete()

        recalc_po_total(po)
        
    return redirect("po_items", po_id=po.id)

# @login_required
# @user_passes_test(is_admin)
# def po_item_delete(request, pk):
#     item = get_object_or_404(POItem, pk=pk)
#     po_id = item.po.id

#     if request.method == "POST":
#         item.delete()

#     return redirect("po_items", po_id=po_id)


# =========================================================
# STOCK MOVEMENTS
# =========================================================

@login_required
@user_passes_test(is_admin)
def stock_movement_list(request):

    if request.method == "POST":

        action = request.POST.get("action")

        # CREATE / STOCK UPDATE
        if action == "create":

            product_id = request.POST.get("product")
            movement_type = request.POST.get("type")
            quantity = int(request.POST.get("quantity") or 0)
            reason = request.POST.get("reason")

            product = Product.objects.filter(id=product_id).first()

            if product and quantity > 0:

                if movement_type == "in":
                    product.stock_qty = (product.stock_qty or 0) + quantity

                elif movement_type == "out":
                    product.stock_qty = max((product.stock_qty or 0) - quantity, 0)

                elif movement_type == "adjustment":
                    product.stock_qty = quantity

                product.save()

                StockMovement.objects.create(
                    product=product,
                    type=movement_type,
                    quantity=quantity,
                    reason=reason
                )

        # DELETE MOVEMENT
        elif action == "delete":

            movement = get_object_or_404(
                StockMovement,
                id=request.POST.get("id")
            )
            movement.delete()

        return redirect("stock_movement_list")

    movements = StockMovement.objects.select_related(
        "product", "sale_item", "po_item"
    ).order_by("-moved_at")

    products = Product.objects.all()

    return render(request, "panel/stock_movement.html", {
        "movements": movements,
        "products": products
    })

@login_required
@user_passes_test(is_admin)
def discounts(request):

    # ================= AUTO EXPIRE =================
    today = timezone.now().date()
    Discount.objects.filter(valid_until__lt=today).update(status="expired")

    # ================= POST =================
    if request.method == "POST":
        action = request.POST.get("action")

        # ================= CREATE =================
        if action == "create":

            discount = Discount.objects.create(
                name=request.POST.get("name"),
                type=request.POST.get("type"),
                value=float(request.POST.get("value") or 0),
                applies_to=request.POST.get("applies_to"),
                status=request.POST.get("status") or "active",
                valid_from=request.POST.get("valid_from") or None,
                valid_until=request.POST.get("valid_until") or None,
            )

            _sync_relations(discount, request)

            messages.success(request, "Discount created successfully")
            return redirect("discounts")

        # ================= UPDATE =================
        elif action == "update":

            d = get_object_or_404(Discount, id=request.POST.get("id"))

            d.name = request.POST.get("name")
            d.type = request.POST.get("type")
            d.value = float(request.POST.get("value") or 0)
            d.applies_to = request.POST.get("applies_to")
            d.status = request.POST.get("status")

            d.valid_from = request.POST.get("valid_from") or None
            d.valid_until = request.POST.get("valid_until") or None

            d.save()

            _sync_relations(d, request, update=True)

            messages.success(request, "Discount updated successfully")
            return redirect("discounts")

        # ================= DELETE =================
        elif action == "delete":
            Discount.objects.filter(id=request.POST.get("id")).delete()
            messages.success(request, "Discount deleted successfully")
            return redirect("discounts")

    # ================= DATA =================
    discounts = Discount.objects.all().order_by("-id")
    categories = Category.objects.all()
    products = Product.objects.all()

    return render(request, "panel/discounts.html", {
        "discounts": discounts,
        "categories": categories,
        "products": products,
        "active_count": discounts.filter(status="active").count(),
        "expired_count": discounts.filter(status="expired").count(),
    })


# ================= RELATION SYNC =================
def _sync_relations(discount, request, update=False):

    applies_to = request.POST.get("applies_to")

    if update:
        discount.categories.clear()
        discount.products.clear()

    if applies_to == "category":
        category_id = request.POST.get("category")
        if category_id:
            discount.categories.add(category_id)

    elif applies_to == "product":
        product_ids = request.POST.getlist("products")
        if product_ids:
            discount.products.set(product_ids)
            
@login_required
@user_passes_test(is_admin)
def category_list(request):

    if request.method == "POST":
        action = request.POST.get("action")

        name = request.POST.get("name")
        description = request.POST.get("description")
        parent_id = request.POST.get("parent")

        parent = None
        if parent_id:
            parent = Category.objects.filter(id=parent_id).first()

        # CREATE
        if action == "create":
            Category.objects.create(
                name=name,
                description=description,
                parent=parent,
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

def update_order_status(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    if request.method == "POST":
        sale.status = request.POST.get("status")
        sale.save()

        return redirect('customer_details', pk=sale.customer.id)