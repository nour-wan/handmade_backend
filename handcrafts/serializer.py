from rest_framework import serializers

from discount.models import Discount
from .models import Handcraft

class HandcraftSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Handcraft
        fields = "__all__"

class DiscounttoHandcraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
class HandcraftWithDiscountSerializer(serializers.ModelSerializer):
    # discounts = DiscounttoHandcraftSerializer(many=True, source='discounthandcraft_set')
    discounts = serializers.SerializerMethodField()
    class Meta:
        model = Handcraft
        # 
        # fields = "__all__"
        fields = ['id', 'handcraft_name', 'handcraft_price', 'handcraft_count', 'handcraft_image', 'discounts']
    def get_discounts(self, obj):
        discounts = Discount.objects.filter(discounthandcraft__handcraft=obj)
        return DiscounttoHandcraftSerializer(discounts, many=True).data       
        