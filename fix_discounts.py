from dmep.models import Sale
from dmep.utils.discounts import calculate_discounted_price

updated_count = 0

for sale in Sale.objects.all():
    for item in sale.sale_items.select_related('product').all():

        if not item.product:
            continue

        price, discount_obj, pct = calculate_discounted_price(item.product)

        original = float(item.unit_price or 0)
        qty = item.quantity or 0

        if discount_obj:
            item.discount_name = discount_obj.name
            item.discount_pct = round(float(pct or 0), 2)
            item.discount_amount = round((original - price) * qty, 2)
            item.line_total = round(price * qty, 2)

            item.save()
            updated_count += 1

            print(f"Updated: {item.product.name} -> {discount_obj.name} ({pct}%)")

        else:
            print(f"No discount: {item.product.name}")

print(f"Done. Updated items: {updated_count}")
