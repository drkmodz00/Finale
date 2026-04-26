# Updated seed.py (prices, discounts, categories, subcategories adjusted)

from dmep.models import (
    Category, Supplier, Cashier, Customer, Product, Discount,
    Sale, SaleItem, StockMovement, PurchaseOrder, POItem,
    HelpCenter, NewsletterSubscriber
)
from django.utils import timezone
from datetime import timedelta, date
import random
from django.core.management.base import BaseCommand
from dmep.utils.discounts import calculate_discounted_price


def run():
    # Clear old data
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    StockMovement.objects.all().delete()
    POItem.objects.all().delete()
    PurchaseOrder.objects.all().delete()
    Discount.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Supplier.objects.all().delete()
    Cashier.objects.all().delete()
    Customer.objects.all().delete()
    NewsletterSubscriber.objects.all().delete()
    HelpCenter.objects.all().delete()

    # =====================================
    # MAIN CATEGORIES
    # =====================================
    men_category = Category.objects.create(
        name='Men Fashion',
        description='All men apparel'
    )

    women_category = Category.objects.create(
        name='Women Fashion',
        description='All women apparel'
    )

    kids_category = Category.objects.create(
        name='Kids Fashion',
        description='Kids clothing and accessories'
    )

    accessories_category = Category.objects.create(
        name='Accessories',
        description='Fashion accessories'
    )

    # =====================================
    # SUBCATEGORIES
    # =====================================
    categories = [
        Category.objects.create(name='T-Shirts', parent=men_category),
        Category.objects.create(name='Polos', parent=men_category),
        Category.objects.create(name='Jeans', parent=men_category),
        Category.objects.create(name='Jackets', parent=men_category),
        Category.objects.create(name='Hoodies', parent=men_category),

        Category.objects.create(name='Dresses', parent=women_category),
        Category.objects.create(name='Blouses', parent=women_category),
        Category.objects.create(name='Skirts', parent=women_category),
        Category.objects.create(name='Formal Wear', parent=women_category),
        Category.objects.create(name='Sleepwear', parent=women_category),

        Category.objects.create(name='Kids Casual Wear', parent=kids_category),
        Category.objects.create(name='Kids School Wear', parent=kids_category),

        Category.objects.create(name='Shoes', parent=accessories_category),
        Category.objects.create(name='Bags', parent=accessories_category),
        Category.objects.create(name='Caps', parent=accessories_category),
        Category.objects.create(name='Socks', parent=accessories_category),
    ]

    # =====================================
    # PRODUCTS WITH BETTER PRICING
    # =====================================
    product_names = [
        'Classic White Shirt',
        'Black Polo Shirt',
        'Slim Fit Jeans',
        'Denim Jacket',
        'Red Summer Dress',
        'Blue Hoodie',
        'Leather Belt',
        'White Sneakers',
        'Black Backpack',
        'Sports Leggings',
        'Kids T-Shirt',
        'Floral Skirt',
        'Cargo Shorts',
        'Formal Blazer',
        'Pajama Set',
        'Cotton Socks',
        'Baseball Cap',
        'Winter Coat',
        'Swim Trunks',
        'Women Handbag'
    ]

    products = []
    for i, name in enumerate(product_names):
        cost_price = random.randint(250, 1200)
        selling_price = cost_price + random.randint(150, 800)

        products.append(
            Product.objects.create(
                category=random.choice(categories),
                name=name,
                sku=f'SKU-{1000+i}',
                barcode=f'BAR-{2000+i}',
                cost_price=cost_price,
                selling_price=selling_price,
                stock_qty=random.randint(25, 120),
                reorder_level=random.randint(5, 20),
                unit='pcs',
                status='active'
            )
        )

    # =====================================
    # DISCOUNTS WITH BETTER VALUES
    # =====================================
    discounts = []

    for i in range(1, 11):
        discount = Discount.objects.create(
            name=f'Season Sale {i}',
            type='percentage',
            value=random.choice([5, 10, 15, 20, 25]),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30),
            applies_to=random.choice(['all', 'category', 'product']),
            status='active'
        )

        discount.categories.add(random.choice(categories))
        discount.products.add(random.choice(products))
        discounts.append(discount)

    for i in range(11, 16):
        discount = Discount.objects.create(
            name=f'Fixed Promo {i}',
            type='fixed',
            value=random.choice([50, 100, 150, 200]),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30),
            applies_to=random.choice(['category', 'product']),
            status='active'
        )

        discount.categories.add(random.choice(categories))
        discount.products.add(random.choice(products))
        discounts.append(discount)

    print('Updated seed data created successfully!')


class Command(BaseCommand):
    help = 'Seed database with improved prices, discounts, and categories'

    def handle(self, *args, **kwargs):
        run()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
