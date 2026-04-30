def recalc_po_total(po):
    total = sum(
        item.qty_ordered * item.unit_cost
        for item in po.po_items.all()
    )
    po.total_cost = total
    po.save()