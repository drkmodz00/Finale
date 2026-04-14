from django.shortcuts import render
from django.db.models import Q

from ..models import Product


def product_list(request):
    q = request.GET.get("q", "")
    products = Product.objects.filter(name__icontains=q) if q else Product.objects.all()

    return render(request, "products/list.html", {
        "products": products
    })


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, "products/detail.html", {"product": product})