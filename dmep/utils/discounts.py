from django.utils import timezone
from decimal import Decimal
from dmep.models import Discount, Product


def get_product_discount(product):
    today = timezone.now().date()

    discounts = Discount.objects.filter(status='active')

    for d in discounts:
        if d.valid_from and d.valid_from > today:
            continue
        if d.valid_until and d.valid_until < today:
            continue

        if d.applies_to == 'all':
            return d

        if d.applies_to == 'category':
            if product.category and product.category in d.categories.all():
                return d

        if d.applies_to == 'product':
            if product in d.products.all():
                return d

    return None


def calculate_discounted_price(product):
    discount = get_product_discount(product)

    if not discount:
        return product.selling_price, None, 0

    price = Decimal(product.selling_price or 0)
    value = Decimal(discount.value or 0)

    if discount.type == 'percentage':
        new_price = price - (price * value / 100)
        percent = int(value)
    else:
        new_price = price - value
        percent = round((value / price) * 100) if price > 0 else 0
    return new_price, discount, percent

def get_sale_products():
    today = timezone.now().date()

    active_discounts = Discount.objects.filter(status='active')

    product_ids = set()

    for discount in active_discounts:

        if discount.valid_from and discount.valid_from > today:
            continue
        if discount.valid_until and discount.valid_until < today:
            continue

        if discount.applies_to == 'all':
            product_ids.update(Product.objects.values_list('id', flat=True))

        elif discount.applies_to == 'category':
            product_ids.update(
                Product.objects.filter(
                    category__in=discount.categories.all()
                ).values_list('id', flat=True)
            )

        elif discount.applies_to == 'product':
            product_ids.update(
                discount.products.values_list('id', flat=True)
            )

    return Product.objects.filter(id__in=product_ids)