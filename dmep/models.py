from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
        
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    def __str__(self):
        return self.name
    
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return self.name
    
# class Cashier(models.Model):
#     # ROLE_CHOICES = [('admin', 'Admin'), ('cashier', 'Cashier'), ('manager', 'Manager')]
#     ROLE_CHOICES = [('admin', 'Admin')]

#     STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]
 
#     full_name = models.CharField(max_length=255)
#     username = models.CharField(max_length=150, unique=True)
#     password_hash = models.CharField(max_length=255)
#     role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
 
#     def set_password(self, raw_password):
#         self.password_hash = make_password(raw_password)

#     def check_password(self, raw_password):
#         return check_password(raw_password, self.password_hash)

#     def __str__(self):
#         return self.full_name

class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.full_name
 
class Product(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('discontinued', 'Discontinued')]
 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    selling_price = models.FloatField(blank=True, null=True)
    stock_qty = models.IntegerField(blank=True, null=True)
    reorder_level = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    img = CloudinaryField('image', blank=True, null=True)
    
    def __str__(self):
        return self.name
 
class Discount(models.Model):
    TYPE_CHOICES = [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')]
    APPLIES_CHOICES = [('all', 'All Products'), ('category', 'Category'), ('product', 'Product')]
 
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    applies_to = models.CharField(max_length=50, choices=APPLIES_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    categories = models.ManyToManyField('Category', blank=True)
    products = models.ManyToManyField('Product', blank=True)
    
    def __str__(self):
        return self.name or f"Discount #{self.id}"
    
class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('refunded', 'Refunded'), 
        ('shipped', 'Shipped'), 
        ('processing', 'Processing'), 
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered')
    ]
    PAYMENT_CHOICES = [('COD', 'Cash on Delivery'), ('GCASH', 'GCash')]

    order_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    guest_id = models.CharField(max_length=255, null=True, blank=True)
    # cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    sale_date = models.DateTimeField(auto_now_add=True)
    subtotal = models.FloatField(blank=True, null=True)
    discount_amount = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    total_amount = models.FloatField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, blank=True, null=True)
    amount_tendered = models.FloatField(blank=True, null=True)
    change_given = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True, default='pending')
    
    def can_cancel(self):
        if not self.sale_date:
            return False
        
        return(
            self.status == 'pending' and 
            timezone.now() - self.sale_date < timedelta(hours=24)
        )
    def __str__(self):
        return f"Sale #{self.id} - {self.customer}"
 
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='sale_items')
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    discount_pct = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)
    discount_name = models.CharField(max_length=255, blank=True, null=True)
    discount_type = models.CharField(max_length=50, blank=True, null=True)
    line_total = models.FloatField()
 
    def __str__(self):
        return f"SaleItem #{self.id} - {self.product}"
    
class StockMovement(models.Model):
    TYPE_CHOICES = [('in', 'Stock In'), ('out', 'Stock Out'), ('adjustment', 'Adjustment'), ('return', 'Return')]
 
    po_item = models.ForeignKey('POItem', on_delete=models.SET_NULL, null=True, blank=True)
    sale_item = models.ForeignKey('SaleItem', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='movements')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    moved_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.type} - {self.product} ({self.quantity})"
 
 
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('received', 'Received'), ('partial', 'Partial'), ('cancelled', 'Cancelled')]
 
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchase_orders')
    order_date = models.DateTimeField(auto_now_add=True)
    received_date = models.DateTimeField(blank=True, null=True)
    total_cost = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
 
    def __str__(self):
        return f"PO #{self.id} - {self.supplier}"
 
 
class POItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='po_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='po_items')
    qty_ordered = models.IntegerField()

    # this should be in purchase order?
    qty_received = models.IntegerField(default=0)


    unit_cost = models.FloatField()
 
    def __str__(self):
        return f"POItem #{self.id} - {self.product}"


# added models

class HelpCenter(models.Model):
    email = models.EmailField(default="support@dmep.com")
    phone = models.CharField(max_length=50, default="+63 9XX XXX XXXX")
    response_time = models.CharField(max_length=100, default="24–48 hours")

    shipping_processing = models.CharField(max_length=100, default="1–2 business days")
    shipping_metro = models.CharField(max_length=100, default="2–5 days")
    shipping_provincial = models.CharField(max_length=100, default="3–10 days")

    returns_days = models.IntegerField(default=7)
    refund_time = models.CharField(max_length=100, default="3–5 business days")
    shipping_refundable = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Help Center Settings"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class OrderTracking(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sale.order_code} - {self.status}"

class OrderStatusHistory(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)