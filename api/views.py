from django.shortcuts import render
from rest_framework import viewsets
from .models import Category, Package, Product, Cart, CartItem
from .serializers import CategorySerializer, PackageSerializer, ProductSerializer, CartSerializer, CartItemSerializer

# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

    def perform_create(self, serializer):
        cart = Cart.objects.get(pk=self.kwargs['cart_pk'])
        serializer.save(cart=cart)
