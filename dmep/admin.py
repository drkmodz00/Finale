from django.contrib import admin
from .models import (
    Category, Supplier, Customer, Product,
    Discount, Sale, SaleItem,
    StockMovement, PurchaseOrder, POItem,
    HelpCenter
)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('line_total',)
    fields = ('product', 'quantity', 'unit_price', 'discount_pct', 'line_total')


class POItemInline(admin.TabularInline):
    model = POItem
    extra = 0
    fields = ('product', 'qty_ordered', 'qty_received', 'unit_cost')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'email', 'contact_person')
    ordering = ('name',)


# @admin.register(Cashier)
# class CashierAdmin(admin.ModelAdmin):
#     list_display = ('id', 'full_name', 'username', 'role', 'status')
#     list_filter = ('role', 'status')
#     search_fields = ('full_name', 'username')
#     ordering = ('full_name',)

#     # show password field in admin form
#     fields = ('full_name', 'username', 'role', 'status', 'password_hash')

#     def save_model(self, request, obj, form, change):
#         raw_password = form.cleaned_data.get('password_hash')

#         # only hash if user typed something
#         if raw_password and not raw_password.startswith('pbkdf2_'):
#             obj.set_password(raw_password)

#         super().save_model(request, obj, form, change)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'email', 'loyalty_points', 'address', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'address')
    ordering = ('full_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'sku', 'category', 'supplier',
        'cost_price', 'selling_price', 'stock_qty', 'reorder_level', 'status', 'created_at',
    )
    list_filter = ('status', 'category', 'supplier')
    search_fields = ('name', 'sku')
    ordering = ('name',)
    autocomplete_fields = ('category', 'supplier')

    def get_search_fields(self, request):
        return ('name', 'sku')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'type', 'value',
        'created_at',
        'valid_from', 'valid_until',
        'applies_to', 'status',
        'get_categories', 'get_products'
    )

    list_filter = ('type', 'status', 'applies_to')
    search_fields = ('name',)
    ordering = ('-valid_until',)

    # ✅ SHOW categories
    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = "Categories"

    # ✅ SHOW products
    def get_products(self, obj):
        return ", ".join([p.name for p in obj.products.all()])
    get_products.short_description = "Products"
    
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sale_date', 'customer',
        'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
        'payment_method', 'status'
    )
    list_filter = ('status', 'payment_method', 'sale_date')
    search_fields = ['customer__full_name']
    ordering = ('-sale_date',)
    readonly_fields = ('sale_date',)
    inlines = (SaleItemInline,)
    date_hierarchy = 'sale_date'

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product', 'quantity', 'unit_price', 'discount_pct', 'line_total')
    search_fields = ('product__name',)
    ordering = ('sale',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'type', 'quantity', 'moved_at', 'reason')
    list_filter = ('type', 'moved_at')
    search_fields = ('product__name', 'reason')
    ordering = ('-moved_at',)
    readonly_fields = ('moved_at',)
    date_hierarchy = 'moved_at'


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'order_date', 'received_date', 'total_cost', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('supplier__name',)
    ordering = ('-order_date',)
    readonly_fields = ('order_date',)
    inlines = (POItemInline,)
    date_hierarchy = 'order_date'


@admin.register(POItem)
class POItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'po', 'product', 'qty_ordered', 'qty_received', 'unit_cost')
    search_fields = ('product__name',)
    ordering = ('po',)

@admin.register(HelpCenter)
class HelpCenterAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "updated_at")

