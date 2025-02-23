from django.shortcuts import render
from rest_framework import viewsets
from .models import Category, Package, Product, Cart, CartItem
from .serializers import CategorySerializer, PackageSerializer, ProductSerializer, CartSerializer, CartItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_user_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

    def perform_create(self, serializer):
        cart = Cart.objects.get(pk=self.kwargs['cart_pk'])
        serializer.save(cart=cart)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_item(self, request, cart_pk=None):
        cart = Cart.objects.get(pk=cart_pk)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            # Initialize existing_item to None
            existing_item = None

            # Get content type and object id from the validated data
            content_type = serializer.validated_data.get('content_type')
            object_id = serializer.validated_data.get('object_id')

            if content_type and object_id:
                existing_item = CartItem.objects.filter(
                    cart=cart,
                    content_type=content_type,
                    object_id=object_id
                ).first()

            if existing_item:
                # Increase quantity of existing item by 1
                existing_item.quantity += 1
                existing_item.save()
                return Response(CartItemSerializer(existing_item).data, status=status.HTTP_200_OK)
            else:
                # Create new cart item with quantity 1
                serializer.save(cart=cart, quantity=1)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
