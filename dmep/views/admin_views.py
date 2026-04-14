from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.contrib import messages
from django.utils import timezone

from ..models import *


# =========================
# ADMIN CHECK
# =========================
def is_admin(user):
    return user.is_staff or user.is_superuser


# =========================
# SUPPLIERS
# =========================
@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    suppliers = Supplier.objects.annotate(product_count=Count("products"))
    return render(request, "admin/suppliers/list.html", {"suppliers": suppliers})


@login_required
@user_passes_test(is_admin)
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    products = supplier.products.all()

    return render(request, "admin/suppliers/detail.html", {
        "supplier": supplier,
        "products": products
    })


# =========================
# CUSTOMERS
# =========================
@login_required
@user_passes_test(is_admin)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sales.select_related().all().order_by("-sale_date")

    total_spent = sales.aggregate(total=Sum("total_amount"))["total"] or 0

    return render(request, "admin/customers/detail.html", {
        "customer": customer,
        "sales": sales,
        "total_spent": total_spent
    })


# =========================
# PRODUCTS (REAL CRUD)
# =========================
@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get("name"),
            sku=request.POST.get("sku"),
            selling_price=request.POST.get("selling_price"),
            cost_price=request.POST.get("cost_price"),
            stock_qty=request.POST.get("stock_qty"),
            status="active"
        )
        messages.success(request, "Product created")
        return redirect("product_create")

    return render(request, "admin/products/create.html")


@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.sku = request.POST.get("sku")
        product.selling_price = request.POST.get("selling_price")
        product.cost_price = request.POST.get("cost_price")
        product.stock_qty = request.POST.get("stock_qty")
        product.save()

        messages.success(request, "Product updated")
        return redirect("product_edit", pk=pk)

    return render(request, "admin/products/edit.html", {"product": product})


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted")
        return redirect("supplier_list")

    return render(request, "admin/products/delete.html", {"product": product})


# =========================
# SALES
# =========================
@login_required
@user_passes_test(is_admin)
def sale_list(request):
    sales = Sale.objects.select_related("customer").all().order_by("-sale_date")

    total_sales = sales.filter(status="completed").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return render(request, "admin/sales/list.html", {
        "sales": sales,
        "total_sales": total_sales
    })


@login_required
@user_passes_test(is_admin)
def sale_create(request):
    return render(request, "admin/sales/create.html")


@login_required
@user_passes_test(is_admin)
def sale_void(request, pk):
    sale = get_object_or_404(Sale, pk=pk)

    if request.method == "POST":
        if sale.status != "voided":
            for item in sale.sale_items.all():
                if item.product:
                    item.product.stock_qty += item.quantity
                    item.product.save()

            sale.status = "voided"
            sale.save()

            messages.warning(request, f"Sale #{sale.id} voided")

        return redirect("sale_list")

    return render(request, "admin/sales/void.html", {"sale": sale})


# =========================
# PURCHASE ORDERS
# =========================
@login_required
@user_passes_test(is_admin)
def po_list(request):
    pos = PurchaseOrder.objects.select_related("supplier").all()
    return render(request, "admin/po/list.html", {"pos": pos})


@login_required
@user_passes_test(is_admin)
def po_create(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        po = PurchaseOrder.objects.create(
            supplier_id=supplier_id,
            status="pending"
        )
        messages.success(request, "PO created")
        return redirect("po_list")

    return render(request, "admin/po/create.html")


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

    return render(request, "admin/po/receive.html", {"po": po})


# =========================
# STOCK MOVEMENTS (SAFE VIEW)
# =========================
@login_required
@user_passes_test(is_admin)
def stock_movement_list(request):
    movements = StockMovement.objects.select_related("product").all().order_by("-moved_at")

    return render(request, "admin/stock/list.html", {
        "movements": movements
    })

@login_required
@user_passes_test(is_admin)
def discount_list(request):
    discounts = Discount.objects.all().order_by("-valid_until")

    return render(request, "admin/discounts/list.html", {
        "discounts": discounts
    })


# =========================
# CREATE DISCOUNT
# =========================
@login_required
@user_passes_test(is_admin)
def discount_create(request):
    if request.method == "POST":
        Discount.objects.create(
            name=request.POST.get("name"),
            type=request.POST.get("type"),
            value=request.POST.get("value"),
            valid_from=request.POST.get("valid_from"),
            valid_until=request.POST.get("valid_until"),
            applies_to=request.POST.get("applies_to"),
            status="active"
        )
        messages.success(request, "Discount created")
        return redirect("discount_list")

    return render(request, "admin/discounts/create.html")


# =========================
# EDIT DISCOUNT
# =========================
@login_required
@user_passes_test(is_admin)
def discount_edit(request, pk):
    discount = get_object_or_404(Discount, pk=pk)

    if request.method == "POST":
        discount.name = request.POST.get("name")
        discount.type = request.POST.get("type")
        discount.value = request.POST.get("value")
        discount.valid_from = request.POST.get("valid_from")
        discount.valid_until = request.POST.get("valid_until")
        discount.applies_to = request.POST.get("applies_to")
        discount.save()

        messages.success(request, "Discount updated")
        return redirect("discount_list")

    return render(request, "admin/discounts/edit.html", {
        "discount": discount
    })


# =========================
# DELETE DISCOUNT
# =========================
@login_required
@user_passes_test(is_admin)
def discount_delete(request, pk):
    discount = get_object_or_404(Discount, pk=pk)

    if request.method == "POST":
        discount.delete()
        messages.success(request, "Discount deleted")
        return redirect("discount_list")

    return render(request, "admin/discounts/delete.html", {
        "discount": discount
    })