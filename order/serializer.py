from rest_framework import serializers
from .models import Order, OrderClothes
class OrderClothesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderClothes
        fields =  ['clothes','quantity','price']



class OrderSerializer(serializers.ModelSerializer):
    # customer = serializers.IntegerField()
    # delivery = serializers.BooleanField()
    # clothes = serializers.ListField(child=OrderClothesSerializer())
    # design = serializers.ListField(child = DiscountSerializer())
    class Meta:
        model = Order
        fields =  '__all__'
    def to_array(order, design_order):
        return {
            "id":order.id,
            "total_price":order.total_price,
            "date":order.date,
            "time":order.time,
            "delivery":order.delivery,
            "location":order.location,
            "latitude":order.latitude,
            "longitude":order.longitude,
            "cost":order.cost,
            "customer_phone" : order.customer_phone,
            "customer":order.customer.id,
            "clothes": OrderClothesSerializer(OrderClothes.objects.filter(order = order.id), many=True).data,
            "design": DesignSerializer.to_array(design_order),
        }  





