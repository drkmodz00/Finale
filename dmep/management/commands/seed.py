from dmep.models import (
    Category, Product, Discount
)
from datetime import timedelta, date
import random
from django.core.management.base import BaseCommand

def run():

    # =====================================
    # MAIN CATEGORIES
    # =====================================
    men_category, _ = Category.objects.get_or_create(
        name='Men Fashion',
        defaults={'description': 'All men apparel'}
    )

    women_category, _ = Category.objects.get_or_create(
        name='Women Fashion',
        defaults={'description': 'All women apparel'}
    )

    kids_category, _ = Category.objects.get_or_create(
        name='Kids Fashion',
        defaults={'description': 'Kids clothing and accessories'}
    )

    accessories_category, _ = Category.objects.get_or_create(
        name='Accessories',
        defaults={'description': 'Fashion accessories'}
    )

    # =====================================
    # SUBCATEGORIES
    # =====================================
    categories = [
        Category.objects.get_or_create(name='T-Shirts', parent=men_category)[0],
        Category.objects.get_or_create(name='Polos', parent=men_category)[0],
        Category.objects.get_or_create(name='Jeans', parent=men_category)[0],
        Category.objects.get_or_create(name='Jackets', parent=men_category)[0],
        Category.objects.get_or_create(name='Hoodies', parent=men_category)[0],

        Category.objects.get_or_create(name='Dresses', parent=women_category)[0],
        Category.objects.get_or_create(name='Blouses', parent=women_category)[0],
        Category.objects.get_or_create(name='Skirts', parent=women_category)[0],
        Category.objects.get_or_create(name='Formal Wear', parent=women_category)[0],
        Category.objects.get_or_create(name='Sleepwear', parent=women_category)[0],

        Category.objects.get_or_create(name='Kids Casual Wear', parent=kids_category)[0],
        Category.objects.get_or_create(name='Kids School Wear', parent=kids_category)[0],

        Category.objects.get_or_create(name='Shoes', parent=accessories_category)[0],
        Category.objects.get_or_create(name='Bags', parent=accessories_category)[0],
        Category.objects.get_or_create(name='Caps', parent=accessories_category)[0],
        Category.objects.get_or_create(name='Socks', parent=accessories_category)[0],
    ]

    # =====================================
    # PRODUCTS
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

        product, created = Product.objects.get_or_create(
            sku=f'SKU-{1000+i}',
            defaults={
                'category': random.choice(categories),
                'name': name,
                'barcode': f'BAR-{2000+i}',
                'cost_price': cost_price,
                'selling_price': selling_price,
                'stock_qty': random.randint(25, 120),
                'reorder_level': random.randint(5, 20),
                'unit': 'pcs',
                'status': 'active'
            }
        )

        products.append(product)

    # =====================================
    # DISCOUNTS
    # =====================================
    for i in range(1, 11):

        discount, _ = Discount.objects.get_or_create(
            name=f'Season Sale {i}',
            defaults={
                'type': 'percentage',
                'value': random.choice([5, 10, 15, 20, 25]),
                'valid_from': date.today(),
                'valid_until': date.today() + timedelta(days=30),
                'applies_to': 'all',
                'status': 'active'
            }
        )

        discount.categories.add(random.choice(categories))
        discount.products.add(random.choice(products))

    for i in range(11, 16):

        discount, _ = Discount.objects.get_or_create(
            name=f'Fixed Promo {i}',
            defaults={
                'type': 'fixed',
                'value': random.choice([50, 100, 150, 200]),
                'valid_from': date.today(),
                'valid_until': date.today() + timedelta(days=30),
                'applies_to': 'category',
                'status': 'active'
            }
        )

        discount.categories.add(random.choice(categories))
        discount.products.add(random.choice(products))

    print("✅ Safe seed completed successfully (no data reset).")


class Command(BaseCommand):
    help = "Safe seed script (no data deletion, no duplicates)"

    def handle(self, *args, **kwargs):
        run()
        self.stdout.write(self.style.SUCCESS("Database safely seeded!"))