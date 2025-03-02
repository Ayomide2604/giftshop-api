from django.shortcuts import redirect, render, get_object_or_404
from rest_framework import viewsets, permissions
from .models import Category, Package, Product, Cart, CartItem, Order, OrderItem, Shipping
from .serializers import CategorySerializer, PackageSerializer, ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, ShippingSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .paginators import CustomPagination
from .services import place_order
import secrets
import requests
from django.conf import settings

# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-created_at')
    serializer_class = CategorySerializer
    pagination_class = CustomPagination


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all().order_by('-created_at')
    serializer_class = PackageSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categories', 'price']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    pagination_class = CustomPagination


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_user_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['delete', 'get'], permission_classes=[IsAuthenticated])
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

    @action(detail=True, methods=['post', 'get'], permission_classes=[IsAuthenticated])
    def increase_quantity(self, request, cart_pk=None, pk=None):
        cart_item = get_object_or_404(CartItem, cart_id=cart_pk, id=pk)
        cart_item.quantity += 1
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'get'], permission_classes=[IsAuthenticated])
    def decrease_quantity(self, request, cart_pk=None, pk=None):
        """Decrease quantity of a specific cart item, delete if quantity is 1"""
        cart_item = get_object_or_404(CartItem, cart_id=cart_pk, id=pk)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)
        else:
            cart_item.delete()
            return Response({"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post', 'get'])
    def place_order(self, request):
        try:
            order = place_order(request.user)
            return Response(OrderSerializer(order).data, status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post', 'get'])
    def initialize_payment(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.payment_status == 'successful':
            return Response({"message": "This order has already been paid for."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a unique reference
        order.reference = f"PAY-{secrets.token_hex(8)}"
        order.save()

        # Paystack API request payload
        payload = {
            "email": request.user.email,
            "amount": int(order.total_price * 100),  # Convert to kobo
            "reference": order.reference,
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        url = "https://api.paystack.co/transaction/initialize"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and "data" in data:
            return Response({"checkout_url": data["data"]["authorization_url"]}, status=status.HTTP_200_OK)
        else:
            return Response({"error": data.get("message", "Payment initialization failed")}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def verify_payment(self, request):
        reference = request.GET.get("reference") or request.GET.get("trxref")

        if not reference:
            return Response({"error": "Reference is required"}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, reference=reference)

        # Verify the transaction with Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200 and data["data"]["status"] == "success":
            order.payment_status = "successful"
            order.status = "processing"
            order.save()
            return Response(
                {"message": "Payment verified successfully",
                    "order_id": order.id, "status": "successful"},
                status=status.HTTP_200_OK
            )
        else:
            order.payment_status = "failed"
            order.status = "pending"
            order.save()
            return Response(
                {"message": "Payment verification failed",
                    "order_id": order.id, "status": "failed"},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)


class ShippingViewSet(viewsets.ModelViewSet):
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
