from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, F
from decimal import Decimal
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, Discount
from .utils.discounts import calculate_discounted_price


# =======================
# CART
# =======================

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product = get_object_or_404(Product, id=product_id)

    # ✅ ALWAYS USE CENTRAL DISCOUNT LOGIC
    final_price, discount_obj, percent = calculate_discounted_price(product)

    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] += 1
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(final_price),                  # discounted price
            'original_price': float(product.selling_price),  # base price
            'discount': float(percent) if percent else 0,
            'qty': 1,
            'image': product.img.url if product.img else ''
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})

    subtotal = 0
    discount_total = 0

    for item in cart.values():
        qty = item.get('qty', 1)
        price = float(item.get('price', 0))
        original = float(item.get('original_price', price))

        subtotal += price * qty
        discount_total += (original - price) * qty

    total = subtotal

    print("CART:", cart)
    print("DISCOUNT TOTAL:", discount_total)

    return render(request, 'user/cart.html', {
        'cart': cart,
        'total': total,
        'discount_total': discount_total,
    })


def cart_count(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(item['qty'] for item in cart.values())}

def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        if action == 'increase':
            cart[pid]['qty'] += 1

        elif action == 'decrease':
            cart[pid]['qty'] -= 1
            if cart[pid]['qty'] <= 0:
                del cart[pid]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'status': 'ok'})


# =======================
# REMOVE ITEM
# =======================

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'status': 'ok'})


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    request.session['cart'] = cart
    return JsonResponse({'status': 'ok'})


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

    # ✅ apply discount to each product
    final_products = []

    for p in products:
        final_price, discount_obj, percent = calculate_discounted_price(p)
        p.final_price = float(final_price)
        p.discount_percent = float(percent) if percent else 0
        p.discount_obj = discount_obj
        final_products.append(p)

    paginator = Paginator(final_products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'user/product/list.html', {
        'categories': categories,
        'products': page_obj,
        'page_obj': page_obj,
        'q': q,
        'selected_category': selected_category,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    final_price, discount_obj, percent = calculate_discounted_price(product)

    return JsonResponse({
        "id": product.id,
        "name": product.name,
        "image": product.img.url if product.img else "",
        "price": float(final_price),
        "original_price": float(product.selling_price or 0),
        "discount_percent": float(percent) if percent else 0,
        "stock_qty": product.stock_qty,
        "status": product.status,
    })
# =======================
# DASHBOARD (STORE FRONT)
# =======================

def dashboard(request):
    products = Product.objects.filter(status='active')[:12]

    sale_products = []

    for p in products:
        final_price, discount_obj, percent = calculate_discounted_price(p)
        p.final_price = float(final_price)
        p.discount_percent = float(percent) if percent else 0

        if discount_obj:
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