from django.shortcuts import render
from rest_framework import viewsets
from .models import Category, Package, Product
from .serializers import CategorySerializer, PackageSerializer, ProductSerializer

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
