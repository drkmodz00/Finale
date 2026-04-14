from django.urls import path
from .views import views_admin, views_user

urlpatterns = [

    # ==================================================
    # 👤 USER SIDE (CUSTOMER / PUBLIC)
    # ==================================================
    path('', views_user.dashboard, name='dashboard'),
    path('about/', views_user.about_us, name='about_us'),
    path('contact/', views_user.contact_us, name='contact_us'),

    # PRODUCTS (USER)
    path('products/', views_user.product_list, name='product_list'),
    path('products/<int:pk>/', views_user.product_detail, name='product_detail'),
    path('search/', views_user.product_search, name='product_search'),

    # CART (USER SESSION CART)
    path('cart/', views_user.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views_user.add_to_cart, name='cart_add'),
    path('cart/update/<int:product_id>/<str:action>/', views_user.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views_user.remove_from_cart, name='cart_remove'),
    path('cart/clear/', views_user.clear_cart, name='clear_cart'),

    # CHECKOUT (USER SIDE POS FLOW)
    path('checkout/', views_user.checkout_view, name='checkout'),
    path('checkout/process/', views_user.process_sale, name='process_sale'),


    # ==================================================
    # 👨‍💼 CASHIER / POS (INTERNAL SALES SYSTEM)
    # ==================================================
    path('pos/cart/', views_user.cart_view, name='pos_cart'),
    path('pos/checkout/', views_user.checkout_view, name='pos_checkout'),
    path('pos/process/', views_user.process_sale, name='pos_process'),


    # ==================================================
    # 🧑 ADMIN SIDE (MANAGEMENT SYSTEM)
    # ==================================================

    # SUPPLIERS
    path('admin-panel/suppliers/', views_admin.supplier_list, name='supplier_list'),
    path('admin-panel/suppliers/<int:pk>/', views_admin.supplier_detail, name='supplier_detail'),

    # CUSTOMERS
    path('admin-panel/customers/<int:pk>/', views_admin.customer_detail, name='customer_detail'),

    # PRODUCTS
    path('admin-panel/products/add/', views_admin.product_create, name='product_create'),
    path('admin-panel/products/<int:pk>/edit/', views_admin.product_edit, name='product_edit'),
    path('admin-panel/products/<int:pk>/delete/', views_admin.product_delete, name='product_delete'),

    # DISCOUNTS
    path('admin-panel/discounts/', views_admin.discount_list, name='discount_list'),

    # SALES
    path('admin-panel/sales/', views_admin.sale_list, name='sale_list'),
    path('admin-panel/sales/new/', views_admin.sale_create, name='sale_create'),
    path('admin-panel/sales/<int:pk>/void/', views_admin.sale_void, name='sale_void'),

    # STOCK
    path('admin-panel/stock/', views_admin.stock_movement_list, name='stock_movement_list'),

    # PURCHASE ORDERS
    path('admin-panel/purchase-orders/', views_admin.po_list, name='po_list'),
    path('admin-panel/purchase-orders/new/', views_admin.po_create, name='po_create'),
    path('admin-panel/purchase-orders/<int:pk>/receive/', views_admin.po_receive, name='po_receive'),
]