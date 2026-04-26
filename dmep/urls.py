from django.urls import path
from .views import customer_views, cashier_views, admin_views

urlpatterns = [
    path('login/', admin_views.login_view, name='login'),
    path('logout/', admin_views.logout_view, name='logout'),
    path('signup/', admin_views.signup_view, name='signup'),

    path('', customer_views.dashboard, name='dashboard'),
    path('products/', customer_views.product_list, name='products'),
    path('products/<int:pk>/', customer_views.product_detail, name='product_detail'),
    path('search/', customer_views.product_search, name='product_search'),

    path('cart/', customer_views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', customer_views.add_to_cart, name='cart_add'),
    path('cart/update/<int:product_id>/<str:action>/', customer_views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', customer_views.remove_from_cart, name='cart_remove'),
    path('cart/clear/', customer_views.clear_cart, name='clear_cart'),
    path("cart/reset/", customer_views.clear_cart_session),
    path("cart/selected/", customer_views.update_selected_items, name="update_selected_items"),

    path('checkout/', customer_views.checkout_view, name='checkout'),
    path('checkout/process/', customer_views.process_sale, name='process_sale'),

    path('orders/', customer_views.orders_view, name='order_history'),
    path('track-order/<uuid:order_code>/', customer_views.track_order, name='track_order'),
    path('cancel-order/<uuid:order_code>/', customer_views.cancel_order, name='cancel_order'),

    path('buy-again/<uuid:order_code>/', customer_views.buy_again, name='buy_again'),

    path("help-center/", customer_views.help_center, name="help_center"),
    path("subscribe-newsletter/", customer_views.subscribe_newsletter, name="subscribe_newsletter"),

    # # ==================================================
    # # Cashier SIDE
    # # ==================================================

    # path('pos/dashboard/', cashier_views.pos_dashboard, name='pos_dashboard'),

    # path("pos/sell/", cashier_views.pos_sell, name="pos_sell"),
    
    # path('pos/cart/', cashier_views.cart_view, name='pos_cart'),
    # path("pos/add/<int:pid>/", cashier_views.add_to_cart, name="pos_add"),
    # path("pos/update/<int:pid>/", cashier_views.update_cart, name="pos_update"),
    # path("pos/remove/<int:pid>/", cashier_views.remove_from_cart, name="pos_remove"),   

    # path('pos/checkout/', cashier_views.checkout_view, name='pos_checkout'),
    
    # path('pos/checkout/process/', cashier_views.process_sale, name='process_checkout'),
    # # path('pos/process/', cashier.process_sale, name='pos_process'),    


    # ==================================================
    # ADMIN SIDE
    # ==================================================

    path('admin-panel/', admin_views.dashboard, name='admin_dashboard'),

    path('admin-panel/categories/', admin_views.category_list, name='category_list'),
    # path('admin-panel/categories/add/', admin_views.category_create, name='category_create'),
    # path('admin-panel/categories/<int:pk>/edit/', admin_views.category_edit, name='category_edit'),
    # path('admin-panel/categories/<int:pk>/delete/', admin_views.category_delete, name='category_delete'),
    
    # =========================================================
    # SUPPLIERS (READ ONLY)
    # =========================================================
    path('admin-panel/suppliers/', admin_views.supplier_list, name='supplier_list'),
    # path('admin-panel/suppliers/add/', admin_views.supplier_create, name='supplier_create'),
    # path('admin-panel/suppliers/<int:pk>/edit/', admin_views.supplier_edit, name='supplier_edit'),
    # path('admin-panel/suppliers/<int:pk>/delete/', admin_views.supplier_delete, name='supplier_delete'),
    
    # =========================================================
    # CUSTOMERS (READ ONLY)
    # =========================================================
    path('admin-panel/customers/', admin_views.customer_list, name='customer_list'),
    path('admin-panel/customers/<int:pk>/', admin_views.customer_detail, name='customer_details'),
    


    # =========================================================
    # PRODUCTS (LIST + URL CRUD)
    # =========================================================
    path('admin-panel/products/', admin_views.product_list, name='product_list'),
    path("admin-panel/products/upsert/", admin_views.product_upsert, name="product_upsert"),
    path('admin-panel/products/<int:pk>/delete/', admin_views.product_delete, name='product_delete'),


    # =========================================================
    # DISCOUNTS (LIST + URL CRUD)
    # =========================================================
    path('admin-panel/discounts/', admin_views.discounts, name='discounts'),
    # path('admin-panel/discounts/add/', admin_views.discount_create, name='discount_create'),
    # path('admin-panel/discounts/<int:pk>/edit/', admin_views.discount_edit, name='discount_edit'),
    # path('admin-panel/discounts/<int:pk>/delete/', admin_views.discount_delete, name='discount_delete'),


    # =========================================================
    # SALES (LIST + ACTION)
    # =========================================================
    path('admin-panel/sales/', admin_views.sale_list, name='sale_list'),
    path('admin-panel/sales/new/', admin_views.sale_create, name='sale_create'),
    path('admin-panel/sales/<int:pk>/void/', admin_views.sale_void, name='sale_void'),
    path('admin-panel/sales/<int:pk>/delete/', admin_views.sale_delete, name='sale_delete'),

    # =========================================================
    # STOCK MOVEMENTS (READ ONLY)
    # =========================================================
    path('admin-panel/stock/', admin_views.stock_movement_list, name='stock_movement_list'),


    # =========================================================
    # PURCHASE ORDERS
    # =========================================================
    path('admin-panel/purchase-orders/', admin_views.po_list, name='po_list'),
    path('admin-panel/purchase-orders/new/', admin_views.po_create, name='po_create'),
    path('admin-panel/purchase-orders/<int:pk>/receive/', admin_views.po_receive, name='po_receive'),
]