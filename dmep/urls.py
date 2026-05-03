from django.urls import path
from .views import customer_views, cashier_views, admin_views

urlpatterns = [
    path('login/', admin_views.login_view, name='login'),
    path('logout/', admin_views.logout_view, name='logout'),

    path('', customer_views.dashboard, name='dashboard'),
    path('products/', customer_views.product_list, name='products'),
    path('products/<int:pk>/', customer_views.product_detail, name='product_detail'),
    path('search/', customer_views.product_search, name='product_search'),

    path('cart/', customer_views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', customer_views.add_to_cart, name='cart_add'),
    path('cart/update/<int:product_id>/<str:action>/', customer_views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', customer_views.remove_from_cart, name='cart_remove'),
    path('cart/reset/', customer_views.clear_cart, name='clear_cart'),
    path("cart/selected/", customer_views.update_selected_items, name="update_selected_items"),

    path('checkout/', customer_views.checkout_view, name='checkout'),
    path('checkout/process/', customer_views.process_sale, name='process_sale'),

    path('orders/', customer_views.orders_view, name='order_history'),
    path('track-order/<uuid:order_code>/', customer_views.track_order, name='track_order'),
    path('cancel-order/<uuid:order_code>/', customer_views.cancel_order, name='cancel_order'),

    path('buy-again/<uuid:order_code>/', customer_views.buy_again, name='buy_again'),

    path("help-center/", customer_views.help_center, name="help_center"),
    path("subscribe-newsletter/", customer_views.subscribe_newsletter, name="subscribe_newsletter"),



    path('admin-panel/', admin_views.dashboard, name='admin_dashboard'),

    path('admin-panel/categories/', admin_views.category_list, name='category_list'),

    path('admin-panel/customers/', admin_views.customer_list, name='customer_list'),
    path('admin-panel/customers/<int:pk>/', admin_views.customer_detail, name='customer_details'),
    path('admin-panel/customers/<int:pk>/delete/', admin_views.customer_delete, name='customer_delete'),
    path('order/<int:sale_id>/update-status/', admin_views.update_order_status, name='update_order_status'),
    

    path("admin-panel/purchase/", admin_views.purchase, name="purchase"),
    path("purchase/add/<int:product_id>/", admin_views.purchase_add, name="purchase_add"),
    path("purchase/remove/<int:product_id>/", admin_views.purchase_remove, name="purchase_remove"),
    path("purchase/checkout/", admin_views.purchase_checkout, name="purchase_checkout"),
    path("purchase/checkout/page/", admin_views.purchase_checkout_page, name="purchase_checkout_page"),
    path("purchase/finalize/", admin_views.purchase_finalize, name="purchase_finalize"),

    path('admin-panel/products/', admin_views.product_list, name='product_list'),
    path("admin-panel/products/upsert/", admin_views.product_upsert, name="product_upsert"),
    path("admin-panel/products/<int:pk>/delete/", admin_views.product_delete, name="product_delete"),


    path('admin-panel/discounts/', admin_views.discounts, name='discounts'),

    path('admin-panel/sales/', admin_views.sale_list, name='sale_list'),
    path('admin-panel/sales/new/', admin_views.sale_create, name='sale_create'),
    path('admin-panel/sales/<int:pk>/void/', admin_views.sale_void, name='sale_void'),
    path('admin-panel/sales/<int:pk>/delete/', admin_views.sale_delete, name='sale_delete'),

    path("admin-panel/stock-movements/", admin_views.stock_movement_list, name="stock_movement_list"),

    path('admin-panel/purchase-orders/', admin_views.po_list, name='po_list'),
    path('admin-panel/purchase-orders/new/', admin_views.po_create, name='po_create'),
    path('admin-panel/purchase-orders/<int:po_id>/receive/', admin_views.po_receive, name='po_receive'),
    path('admin-panel/purchase-orders/<int:po_id>/update/', admin_views.po_update, name='po_update'),
    path('admin-panel/purchase-orders/<int:po_id>/delete/', admin_views.po_delete, name='po_delete'),

    path('po/<int:po_id>/items/', admin_views.po_items, name='po_items'),
    path('po/<int:po_id>/items/add/', admin_views.po_item_add, name='po_item_add'),
    path('po/item/<int:pk>/update/', admin_views.po_item_update, name='po_item_update'),
    path('po/item/<int:pk>/delete/', admin_views.po_item_delete, name='po_item_delete'),

    path("debug/reset-session/", customer_views.reset_session),
    path("pos-terminal/", admin_views.pos_terminal, name="pos_terminal"),
]