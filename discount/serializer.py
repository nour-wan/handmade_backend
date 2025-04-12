from rest_framework import serializers

from handcrafts.serializer import HandcraftSerializer

from .models import Discount, DiscountHandcraft

class DiscountHandcraftSerializer(serializers.ModelSerializer):
    handcraft = HandcraftSerializer(read_only=True)
    class Meta:
        model = DiscountHandcraft
        fields = '__all__'  
        
class DiscountSerializer(serializers.ModelSerializer):
    handcrafts = DiscountHandcraftSerializer(many=True, source='discounthandcraft_set', read_only=True)
    class Meta:
        model = Discount
        fields = ['name', 'precentage', 'from_date', 'to_date', 'count', 'handcrafts']
        


              
      
    # handcrafts = HandcraftSerializer(many=True, source='discounthandcraft_set')

    # class Meta:
    #     model = Discount
    #     fields = ['id', 'maker', 'name', 'precentage', 'from_date', 'to_date', 'count', 'handcrafts']