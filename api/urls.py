from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'packages', views.PackageViewSet)
router.register(r'products', views.ProductViewSet)

category_router = routers.NestedDefaultRouter(
    router, r'categories', lookup='category')
category_router.register(
    r'packages', views.PackageViewSet, basename='category-packages')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
]
