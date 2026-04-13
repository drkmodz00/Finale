from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, F
from decimal import Decimal
from django.core.paginator import Paginator

from .models import Product, Category, Discount
from .utils.discounts import calculate_discounted_price


# =======================
# CART
# =======================

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product = get_object_or_404(Product, id=product_id)
    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] += 1
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.selling_price),
            'qty': 1,
            'image': product.img.url if product.img else ''
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())

    return render(request, 'user/cart.html', {
        'cart': cart,
        'total': total
    })


def cart_count(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(item['qty'] for item in cart.values())}


# =======================
# PRODUCTS
# =======================
def product_search(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query) if query else Product.objects.none()

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(status='active').select_related('category')

    q = request.GET.get('q', '')
    selected_category = request.GET.get('category')

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q)
        )

    if selected_category:
        products = products.filter(category_id=selected_category)

    # ✅ FIRST build list
    final_products = []

    for p in products:
        final_price, discount, percent = calculate_discounted_price(p)
        p.final_price = final_price
        p.discount_percent = percent
        final_products.append(p)

    # ✅ THEN paginate
    paginator = Paginator(final_products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'user/product/list.html', {
        'categories': categories,
        'products': page_obj,   # ✅ use paginated data
        'page_obj': page_obj,
        'q': q,
        'selected_category': selected_category,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    final_price, discount, percent = calculate_discounted_price(product)
    product.final_price = final_price
    product.discount_percent = percent

    return render(request, 'user/product/detail.html', {
        'product': product
    })


# =======================
# DASHBOARD (STORE FRONT)
# =======================

def dashboard(request):
    products = Product.objects.filter(status='active')[:12]

    sale_products = []

    for p in products:
        final_price, discount, percent = calculate_discounted_price(p)
        p.final_price = final_price
        p.discount_percent = percent
        p.discount_obj = discount

        if discount:
            sale_products.append(p)

    return render(request, "user/dashboard.html", {
        "sale_products": sale_products
    })


# =======================
# STATIC PAGES
# =======================

def about_us(request):
    return render(request, 'user/about.html')


def contact_us(request):
    return render(request, 'user/contact.html')