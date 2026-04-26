from django.utils import timezone
from django.db.models import Q
from ..models import Discount


# def get_applicable_discount(product):
#     today = timezone.now().date()

#     discounts = Discount.objects.filter(
#         status="active"
#     ).filter(
#         Q(valid_from__isnull=True) | Q(valid_from__lte=today),
#         Q(valid_until__isnull=True) | Q(valid_until__gte=today),
#     ).prefetch_related("products", "categories")

#     price = float(product.selling_price or 0)
#     product_id = product.id
#     category_id = product.category_id

#     best = None
#     best_price = price

#     # 🔥 PRIORITY ORDER (IMPORTANT)
#     for priority in ["product", "category", "all"]:

#         for d in discounts:

#             if d.applies_to != priority:
#                 continue

#             eligible = False

#             # PRODUCT LEVEL
#             if priority == "product":
#                 eligible = d.products.filter(id=product_id).exists()

#             # CATEGORY LEVEL
#             elif priority == "category":
#                 eligible = d.categories.filter(id=category_id).exists() if category_id else False

#             # ALL LEVEL
#             elif priority == "all":
#                 eligible = True

#             if not eligible:
#                 continue

#             # CALCULATE PRICE
#             if d.type == "percentage":
#                 final_price = price - (price * (float(d.value or 0) / 100))
#             else:
#                 final_price = max(0, price - float(d.value or 0))

#             if final_price < best_price:
#                 best_price = final_price
#                 best = d

#     return best

def calculate_discounted_price(product):

    today = timezone.now().date()

    discounts = Discount.objects.filter(status="active").filter(
        (Q(valid_from__isnull=True) | Q(valid_from__lte=today)),
        (Q(valid_until__isnull=True) | Q(valid_until__gte=today))
    )

    best_discount = None
    best_price = product.selling_price or 0
    best_pct = 0

    base_price = float(product.selling_price or 0)

    for d in discounts:

        applies = False

        # ALL PRODUCTS
        if d.applies_to == "all":
            applies = True

        # CATEGORY
        elif d.applies_to == "category":
            applies = d.categories.filter(id=product.category_id).exists()

        # PRODUCT
        elif d.applies_to == "product":
            applies = d.products.filter(id=product.id).exists()

        if not applies:
            continue

        # compute price
        if d.type == "percentage":
            new_price = base_price - (base_price * (d.value / 100))
            pct = d.value

        else:  # fixed
            new_price = base_price - d.value
            pct = (d.value / base_price) * 100 if base_price else 0

        if new_price < best_price:
            best_price = new_price
            best_discount = d
            best_pct = pct

    return best_price, best_discount, best_pct