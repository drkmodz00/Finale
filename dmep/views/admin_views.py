from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone

from ..models import *

def is_admin(user):
    return user.is_staff or user.is_superuser


# =========================
# PRODUCTS MANAGEMENT
# =========================

@login_required
@user_passes_test(is_admin)
def product_list_admin(request):
    products = Product.objects.all()
    return render(request, "admin/products/list.html", {"products": products})


# =========================
# SUPPLIERS
# =========================

@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    suppliers = Supplier.objects.annotate(product_count=Count("products"))
    return render(request, "admin/suppliers/list.html", {"suppliers": suppliers})


# =========================
# PURCHASE ORDERS
# =========================

@login_required
@user_passes_test(is_admin)
def po_list(request):
    pos = PurchaseOrder.objects.all()
    return render(request, "admin/po/list.html", {"pos": pos})


# =========================
# DISCOUNTS
# =========================

@login_required
@user_passes_test(is_admin)
def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, "admin/discounts/list.html", {"discounts": discounts})


# =========================
# REPORTS
# =========================

@login_required
@user_passes_test(is_admin)
def sales_report(request):
    total_sales = Sale.objects.filter(status="completed").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return render(request, "admin/reports/sales.html", {
        "total_sales": total_sales
    })