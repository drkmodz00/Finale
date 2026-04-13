from django import forms
from django.forms import inlineformset_factory
from .models import (
    Category, Supplier, Customer, Product, Discount,
    Sale, SaleItem, StockMovement, PurchaseOrder, POItem
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'phone', 'email', 'loyalty_points']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'supplier', 'sku', 'barcode',
            'cost_price', 'selling_price', 'stock_qty',
            'reorder_level', 'unit', 'status'
        ]


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['name', 'type', 'value', 'valid_from', 'valid_until', 'applies_to', 'status']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'cashier', 'customer', 'discount',
            'payment_method', 'amount_tendered',
            'discount_amount', 'tax_amount', 'status'
        ]


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price', 'discount_pct']


SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem,
    form=SaleItemForm,
    extra=3,
    can_delete=True
)


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'cashier', 'type', 'quantity', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'cashier', 'status']


class POItemForm(forms.ModelForm):
    class Meta:
        model = POItem
        fields = ['product', 'qty_ordered', 'qty_received', 'unit_cost']


POItemFormSet = inlineformset_factory(
    PurchaseOrder, POItem,
    form=POItemForm,
    extra=3,
    can_delete=True
)