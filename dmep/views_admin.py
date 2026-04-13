from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction

from .models import *
from .forms import PurchaseOrderForm, POItemFormSet, ProductForm, DiscountForm, SaleForm, SaleItemFormSet



# =======================
# PERMISSION CHECK
# =======================

def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sales.order_by('-sale_date')[:10]
    total_spent = customer.sales.filter(status='completed').aggregate(t=Sum('total_amount'))['t'] or 0
    return render(request, 'user/customer/detail.html', {
        'customer': customer, 'sales': sales, 'total_spent': total_spent
    })
# =======================
# SUPPLIERS
# =======================

@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    q = request.GET.get('q', '')
    suppliers = Supplier.objects.annotate(product_count=Count('products'))

    if q:
        suppliers = suppliers.filter(Q(name__icontains=q))

    paginator = Paginator(suppliers, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin/supplier/list.html', {
        'page_obj': page
    })


@login_required
@user_passes_test(is_admin)
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    products = supplier.products.all()

    return render(request, 'admin/supplier/detail.html', {
        'supplier': supplier,
        'products': products
    })


# =======================
# SALES
# =======================

@login_required
@user_passes_test(is_admin)
def sale_list(request):
    sales = Sale.objects.select_related('customer')

    total = sales.filter(status='completed').aggregate(
        t=Sum('total_amount')
    )['t'] or 0

    return render(request, 'admin/sale/list.html', {
        'sales': sales,
        'total_revenue': total
    })

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def sale_create(request):
    form = SaleForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, prefix='items')
    
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            sale = form.save(commit=False)
            sale.status = 'completed'
            sale.save()  # Save first to get an ID for the foreign keys
            
            items = formset.save(commit=False)
            calculated_subtotal = 0
            
            for item in items:
                item.sale = sale
                # Logic: (Qty * Price) - Discount
                item.line_total = round(item.quantity * item.unit_price * (1 - (item.discount_pct or 0) / 100), 2)
                item.save()
                
                # UPDATE STOCK: Decrease inventory
                if item.product:
                    item.product.stock_qty = (item.product.stock_qty or 0) - item.quantity
                    item.product.save()
                
                calculated_subtotal += item.line_total
            
            # Finalize Sale Totals
            sale.subtotal = calculated_subtotal
            sale.total_amount = calculated_subtotal - (sale.discount_amount or 0) + (sale.tax_amount or 0)
            sale.save()
            
            messages.success(request, f'Sale #{sale.id} recorded successfully.')
            return redirect('sale_detail', pk=sale.pk)
            
    return render(request, 'user/sale/form.html', {
        'form': form, 'formset': formset, 'title': 'New Sale'
    })

@transaction.atomic
def sale_void(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST' and sale.status != 'voided':
        # REVERSE STOCK: Put items back in inventory
        for item in sale.sale_items.all():
            if item.product:
                item.product.stock_qty += item.quantity
                item.product.save()
        
        sale.status = 'voided'
        sale.save()
        messages.warning(request, f'Sale #{pk} has been voided and stock returned.')
        return redirect('sale_list')
        
    return render(request, 'user/confirm_delete.html', {
        'object': sale, 'type': 'Sale', 'action': 'Void'
    })
# =======================
# PURCHASE ORDERS
# =======================

@login_required
@user_passes_test(is_admin)
def po_list(request):
    pos = PurchaseOrder.objects.select_related('supplier')

    paginator = Paginator(pos.order_by('-order_date'), 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin/po/list.html', {
        'page_obj': page
    })


@login_required
@user_passes_test(is_admin)
@transaction.atomic
def po_create(request):
    form = PurchaseOrderForm(request.POST or None)
    formset = POItemFormSet(request.POST or None, prefix='items')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            po = form.save()
            items = formset.save(commit=False)

            total = 0

            for item in items:
                item.po = po
                item.save()
                total += item.qty_ordered * item.unit_cost

            po.total_cost = total
            po.save()

            messages.success(request, "PO created")
            return redirect('po_list')

    return render(request, 'admin/po/form.html', {
        'form': form,
        'formset': formset
    })


@login_required
@user_passes_test(is_admin)
def po_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        for item in po.po_items.all():
            qty = int(request.POST.get(f'qty_{item.id}', 0))

            item.qty_received = qty
            item.save()

            item.product.stock_qty += qty
            item.product.save()

        po.status = 'received'
        po.received_date = timezone.now()
        po.save()

        return redirect('po_list')

    return render(request, 'admin/po/receive.html', {
        'po': po
    })

@login_required
@user_passes_test(is_admin)
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product created.')
        return redirect('product_list')
    return render(request, 'user/product/form.html', {'form': form, 'title': 'Add Product'})

@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product updated.')
        return redirect('product_detail', pk=pk)
    return render(request, 'user/product/form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('product_list')
    return render(request, 'user/confirm_delete.html', {'object': product, 'type': 'Product'})

@login_required
@user_passes_test(is_admin)
def discount_list(request):
    discounts = Discount.objects.all().order_by('-valid_until')
    return render(request, 'user/discount/list.html', {'discounts': discounts})

@login_required
@user_passes_test(is_admin)
def discount_create(request):
    form = DiscountForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Discount created.')
        return redirect('discount_list')
    return render(request, 'user/discount/form.html', {'form': form, 'title': 'Add Discount'})

@login_required
@user_passes_test(is_admin)
def discount_edit(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    form = DiscountForm(request.POST or None, instance=discount)
    if form.is_valid():
        form.save()
        messages.success(request, 'Discount updated.')
        return redirect('discount_list')
    return render(request, 'user/discount/form.html', {'form': form, 'title': 'Edit Discount'})

@login_required
@user_passes_test(is_admin)
def discount_delete(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    if request.method == 'POST':
        discount.delete()
        messages.success(request, 'Discount deleted.')
        return redirect('discount_list')
    return render(request, 'user/confirm_delete.html', {'object': discount, 'type': 'Discount'})

@login_required
@user_passes_test(is_admin)
def stock_movement_list(request):
    q = request.GET.get('q', '')
    movement_type = request.GET.get('type', '')
    movements = StockMovement.objects.select_related('product', 'cashier')
    if q:
        movements = movements.filter(product__name__icontains=q)
    if movement_type:
        movements = movements.filter(type=movement_type)
    paginator = Paginator(movements.order_by('-moved_at'), 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'user/stock/list.html', {
        'page_obj': page, 'q': q, 'selected_type': movement_type
    })