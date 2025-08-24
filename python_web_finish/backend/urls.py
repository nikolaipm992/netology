from django.urls import path
from .views import *

app_name = 'backend'

urlpatterns = [
    path('user/register', RegisterAccountView.as_view(), name='user-register'),
    path('user/login', LoginAccountView.as_view(), name='user-login'),

    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('import/products', ImportProductsView.as_view(), name='import-products'),

    path('basket', BasketView.as_view(), name='basket'),

    path('user/contacts', ContactView.as_view(), name='user-contacts'),

    path('orders', OrderView.as_view(), name='orders-list-create'), 
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),

    path('supplier/orders', SupplierOrdersView.as_view(), name='supplier-orders'),
    path('supplier/orders/<int:order_id>/status', UpdateOrderStatusView.as_view(), name='update-order-status'),
]