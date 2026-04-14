from django.urls import path
from . import views_user, views_admin

urlpatterns = [

    # ======================
    # USER SIDE
    # ======================
    path('', views_user.dashboard, name='dashboard'),
    path('about/', views_user.about_us, name='about_us'),
    path('contact/', views_user.contact_us, name='contact_us'),

    path('cart/', views_user.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views_user.add_to_cart, name='cart_add'),
    path('cart/update/<int:product_id>/<str:action>/', views_user.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views_user.remove_from_cart, name='remove_cart'),

    path('search/', views_user.product_search, name='product-search'),
    path('products/', views_user.product_list, name='product_list'),
    path('products/<int:pk>/', views_user.product_detail, name='product_detail'),


    # ======================
    # ADMIN SIDE (PROTECTED)
    # ======================
    path('admin/suppliers/', views_admin.supplier_list, name='supplier_list'),
    path('admin/suppliers/<int:pk>/', views_admin.supplier_detail, name='supplier_detail'),

    path('admin/customers/<int:pk>/', views_admin.customer_detail, name='customer_detail'),

    path('admin/products/add/', views_admin.product_create, name='product_create'),
    path('admin/products/<int:pk>/edit/', views_admin.product_edit, name='product_edit'),
    path('admin/products/<int:pk>/delete/', views_admin.product_delete, name='product_delete'),

    path('admin/discounts/', views_admin.discount_list, name='discount_list'),

    path('admin/sales/', views_admin.sale_list, name='sale_list'),
    path('admin/sales/new/', views_admin.sale_create, name='sale_create'),
    path('admin/sales/item/', views_admin.sale_void, name='sale_void'),



    path('admin/stock/', views_admin.stock_movement_list, name='stock_movement_list'),

    path('admin/purchase-orders/', views_admin.po_list, name='po_list'),
    path('admin/purchase-orders/new/', views_admin.po_create, name='po_create'),
    path('admin/purchase-orders/<int:pk>/receive/', views_admin.po_receive, name='po_receive'),
]