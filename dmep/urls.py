from django.urls import path
from .views import customer_views, cashier_views, admin_views
urlpatterns = [

    path('', customer_views.dashboard, name='dashboard'),
    path('products/', customer_views.product_list, name='product_list'),
    path('products/<int:pk>/', customer_views.product_detail, name='product_detail'),
    path('search/', customer_views.product_search, name='product_search'),

    path('cart/', customer_views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', customer_views.add_to_cart, name='cart_add'),
    path('cart/update/<int:product_id>/<str:action>/', customer_views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', customer_views.remove_from_cart, name='cart_remove'),
    path('cart/clear/', customer_views.clear_cart, name='clear_cart'),

    path('checkout/', customer_views.checkout_view, name='checkout'),
    path('checkout/process/', customer_views.process_sale, name='process_sale'),

    # ==================================================
    #  CASHIER / POS
        # ==================================================
    path('pos/cart/', cashier_views.cart_view, name='pos_cart'),
    path('pos/checkout/', cashier_views.checkout_view, name='pos_checkout'),
    path('pos/process/', cashier_views.process_sale, name='pos_process'),    

    # ==================================================
    # ADMIN SIDE
    # ==================================================

    path('admin-panel/suppliers/', admin_views.supplier_list, name='supplier_list'),
    path('admin-panel/suppliers/<int:pk>/', admin_views.supplier_detail, name='supplier_detail'),

    path('admin-panel/customers/<int:pk>/', admin_views.customer_detail, name='customer_detail'),

    path('admin-panel/products/add/', admin_views.product_create, name='product_create'),
    path('admin-panel/products/<int:pk>/edit/', admin_views.product_edit, name='product_edit'),
    path('admin-panel/products/<int:pk>/delete/', admin_views.product_delete, name='product_delete'),

    path('admin-panel/discounts/', admin_views.discount_list, name='discount_list'),

    path('admin-panel/sales/', admin_views.sale_list, name='sale_list'),
    path('admin-panel/sales/new/', admin_views.sale_create, name='sale_create'),
    path('admin-panel/sales/<int:pk>/void/', admin_views.sale_void, name='sale_void'),

    path('admin-panel/stock/', admin_views.stock_movement_list, name='stock_movement_list'),

    path('admin-panel/purchase-orders/', admin_views.po_list, name='po_list'),
    path('admin-panel/purchase-orders/new/', admin_views.po_create, name='po_create'),
    path('admin-panel/purchase-orders/<int:pk>/receive/', admin_views.po_receive, name='po_receive'),
]