from rest_framework import serializers
from .models import Order, OrderHandcraft
from handcrafts.models import Handcraft
from handcrafts.serializer import HandcraftSerializer
class OrderHandcraftSerializer(serializers.ModelSerializer):
    handcraft = HandcraftSerializer()
    class Meta:
        model = OrderHandcraft
        fields =  ['handcraft','quantity','price']



class OrderSerializer(serializers.ModelSerializer):
    orderhandcrafts=OrderHandcraftSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'full_price',
                  'date_of_order', 'time_of_order', 
                  'delivery', 'customer_phone',     
                  'customer', 'orderhandcrafts'] 
        def to_representation(self, instance):
            representation = super().to_representation(instance)
            representation['customer'] = instance.customer.id
            return representation
            
        # fields =  '__all__'
    # def to_array(order):
    #     return {
    #         "id":order.id,
    #         "full_price":order.full_price,
    #         "date_of_order":order.date_of_order,
    #         "time_of_order":order.time_of_order,
    #         "delivery":order.delivery,
    #         "cost_for_pice":order.cost_for_pice,
    #         "customer_phone" : order.customer_phone,
    #         "customer":order.customer.id,
    #     }  





