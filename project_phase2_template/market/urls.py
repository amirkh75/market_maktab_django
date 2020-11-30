from django.urls import path, re_path

from . import views

urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    path('product/list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_show_by_id, name='product_list'),
    path('product/<int:product_id>/edit_inventory/', views.product_edit_inventory_id, name='product_edit_inventory_id'),
    # TODO: insert other url paths
    # path(...
    # path(...
    # path(...
]
