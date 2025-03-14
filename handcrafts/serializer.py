from decimal import Decimal
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
    discounted_price = serializers.SerializerMethodField()
    class Meta:
        model = Handcraft
        # 
        # fields = "__all__"
        fields = ['id', 'handcraft_name', 'handcraft_price', 'handcraft_count', 'handcraft_image', 'discounts','discounted_price']
    def get_discounts(self, obj):
        discounts = Discount.objects.filter(discounthandcraft__handcraft=obj)
        return DiscounttoHandcraftSerializer(discounts, many=True).data       
    def get_discounted_price(self, obj):
        discounts = Discount.objects.filter(discounthandcraft__handcraft=obj)
        original_price = obj.handcraft_price  # لا حاجة لتحويله إلى Decimal إذا كان بالفعل Decimal
        if discounts.exists():
            for discount in discounts:
                discount_percentage = Decimal(discount.precentage) / Decimal(100)
                original_price -= original_price * discount_percentage
        return round(original_price, 2)