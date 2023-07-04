from rest_framework import serializers

from .serializer_fields import IntervalField


class PriceSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    amount = serializers.DecimalField(
        source="unit_amount_decimal", max_digits=8, decimal_places=2, required=True
    )
    interval = IntervalField()


class UniqueSellingPointSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True)


class ProductUtilSerializer(serializers.Serializer):
    id = serializers.CharField(source="product.id")
    name = serializers.CharField(source="product.name")
    unique_selling_points = UniqueSellingPointSerializer(many=True)
    featured = serializers.BooleanField(required=True)
    prices = PriceSerializer(source="product.prices", many=True)


class CheckoutSessionSerializer(serializers.Serializer):
    price_id = serializers.CharField(required=True)


class CheckoutSessionResponseSerializer(serializers.Serializer):
    checkout_session_url = serializers.CharField(source="url")


class ProductIntervalSerializer(serializers.Serializer):
    products = ProductUtilSerializer(many=True)
    intervals = serializers.ListField()
