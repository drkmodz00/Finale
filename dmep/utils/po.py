from django.db.models import F, Sum, ExpressionWrapper, FloatField

def recalc_po_total(po):
    total = po.po_items.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('qty_ordered') * F('unit_cost'),
                output_field=FloatField()
            )
        )
    )['total'] or 0

    po.total_cost = total
    po.save(update_fields=['total_cost'])