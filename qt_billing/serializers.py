from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)



class PlanSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    product = ProductSerializer()
    amount = serializers.DecimalField(max_digits=6, decimal_places=2, required=True)


