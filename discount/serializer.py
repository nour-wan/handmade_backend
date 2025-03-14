from rest_framework import serializers
from .models import Discount, DiscountHandcraft

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
        
        
class DiscountHandcraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountHandcraft
        fields = '__all__'        