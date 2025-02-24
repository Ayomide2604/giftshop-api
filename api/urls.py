from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'packages', views.PackageViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')


category_router = routers.NestedDefaultRouter(
    router, r'categories', lookup='category')
category_router.register(
    r'packages', views.PackageViewSet, basename='category-packages')

cart_router = routers.NestedDefaultRouter(
    router, r'carts', lookup='cart')
cart_router.register(
    r'items', views.CartItemViewSet, basename='cart-items')

order_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
order_router.register(r'items', views.OrderItemViewSet, basename='order-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
    path('', include(cart_router.urls)),
    path('', include(order_router.urls)),
]
