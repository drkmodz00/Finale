from dmep.models import Supplier
from django.db.models import Count

dupes = (
    Supplier.objects.values('phone')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

for d in dupes:
    phone = d['phone']
    suppliers = Supplier.objects.filter(phone=phone).order_by('id')

    keep = suppliers.first()
    duplicates = suppliers[1:]

    for s in duplicates:
        s.phone = f"OLD_{s.id}_{phone}"
        s.save()

print("DONE FIXING SUPPLIER DUPLICATES")