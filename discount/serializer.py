from rest_framework import serializers

from handcrafts.serializer import HandcraftSerializer

from .models import Discount, DiscountHandcraft

class DiscountSerializer(serializers.ModelSerializer):
    handcrafts = HandcraftSerializer(many=True, source='discounthandcraft_set')
    class Meta:
        model = Discount
        fields = '__all__'
        


              
class DiscountHandcraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountHandcraft
        fields = '__all__'        
    # handcrafts = HandcraftSerializer(many=True, source='discounthandcraft_set')

    # class Meta:
    #     model = Discount
    #     fields = ['id', 'maker', 'name', 'precentage', 'from_date', 'to_date', 'count', 'handcrafts']