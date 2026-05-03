from django.db import transaction
from ..models import StockMovement


def stock_out(product, qty, sale_item=None, reason="Sale"):

    if qty <= 0:
        return

    with transaction.atomic():

        product.refresh_from_db()

        if product.stock_qty is None:
            product.stock_qty = 0

        if product.stock_qty < qty:
            raise ValueError("Insufficient stock")

        product.stock_qty -= qty
        product.save()

        StockMovement.objects.create(
            product=product,
            sale_item=sale_item,
            type="out",
            quantity=qty,
            reason=reason
        )


def stock_in(product, qty, po_item=None, reason="Restock"):

    if qty <= 0:
        return

    with transaction.atomic():

        product.refresh_from_db()

        product.stock_qty = (product.stock_qty or 0) + qty
        product.save()

        StockMovement.objects.create(
            product=product,
            po_item=po_item,
            type="in",
            quantity=qty,
            reason=reason
        )

def stock_return(product, qty, sale_item=None, reason="Return"):
    if qty <= 0:
        return

    product.stock_qty = (product.stock_qty or 0) + qty
    product.save()

    StockMovement.objects.create(
        product=product,
        sale_item=sale_item,
        type="in",   # 🔥 treat return as stock IN for reporting consistency
        quantity=qty,
        reason=reason
    )