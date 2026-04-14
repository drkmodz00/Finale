from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from ..utils.discounts import calculate_discounted_price

from ..models import Product, Category


def product_list(request):
    q = request.GET.get("q", "")
    category_id = request.GET.get("category")

    products = Product.objects.all()

    selected_category = category_id or ""
    active_parent_id = None

    for product in products:
        final_price, discount_obj, percent = calculate_discounted_price(product)

        product.final_price = final_price
        product.discount_percent = percent
        product.discount_obj = discount_obj
    # Search
    if q:
        products = products.filter(name__icontains=q)

    # Category filter
    if category_id:
        products = products.filter(category_id=category_id)

        try:
            selected_cat = Category.objects.get(id=category_id)
            active_parent_id = selected_cat.parent_id
        except Category.DoesNotExist:
            pass

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Only top-level categories with their subcategories
    categories = Category.objects.filter(parent__isnull=True).prefetch_related("subcategories")

    return render(request, "user/products/list.html", {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "categories": categories,
        "q": q,
        "selected_category": selected_category,
        "active_parent_id": active_parent_id,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "user/products/detail.html", {"product": product})