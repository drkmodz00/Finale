from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='categories/', blank=True, null=True)

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
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return self.name
    
class Cashier(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('cashier', 'Cashier'), ('manager', 'Manager')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]
 
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
 
    def __str__(self):
        return self.full_name

class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
 
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
    img = models.ImageField(upload_to='products/', blank=True, null=True)
 
    is_new = models.BooleanField(default=False)
    is_best = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
 
class Discount(models.Model):
    TYPE_CHOICES = [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')]
    APPLIES_CHOICES = [('all', 'All Products'), ('category', 'Category'), ('product', 'Product')]
 
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    applies_to = models.CharField(max_length=50, choices=APPLIES_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    categories = models.ManyToManyField('Category', blank=True)
    products = models.ManyToManyField('Product', blank=True)
    
    def __str__(self):
        return self.name or f"Discount #{self.discount_id}"
    
class Sale(models.Model):
    STATUS_CHOICES = [('completed', 'Completed'), ('voided', 'Voided'), ('refunded', 'Refunded')]
    PAYMENT_CHOICES = [('cash', 'Cash'), ('card', 'Card'), ('gcash', 'GCash'), ('maya', 'Maya')]
 
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
 
    def __str__(self):
        return f"Sale #{self.id} - {self.customer}"
 
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='sale_items')
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    discount_pct = models.FloatField(default=0)
    line_total = models.FloatField()
 
    def __str__(self):
        return f"SaleItem #{self.id} - {self.product}"
    
class StockMovement(models.Model):
    TYPE_CHOICES = [('in', 'Stock In'), ('out', 'Stock Out'), ('adjustment', 'Adjustment'), ('return', 'Return')]
 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    moved_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.type} - {self.product} ({self.quantity})"
 
 
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('received', 'Received'), ('partial', 'Partial'), ('cancelled', 'Cancelled')]
 
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchase_orders')
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')
    order_date = models.DateTimeField(auto_now_add=True)
    received_date = models.DateTimeField(blank=True, null=True)
    total_cost = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
 
    def __str__(self):
        return f"PO #{self.po_id} - {self.supplier}"
 
 
class POItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='po_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='po_items')
    qty_ordered = models.IntegerField()
    qty_received = models.IntegerField(default=0)
    unit_cost = models.FloatField()
 
    def __str__(self):
        return f"POItem #{self.po_item_id} - {self.product}"