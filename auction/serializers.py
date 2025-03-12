from rest_framework import serializers
from .models import Maker, Handcraft, Auction, MakerAuction, AuctionHandcraft



class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = '__all__'

class MakerAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakerAuction
        fields = '__all__'

class AuctionHandcraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionHandcraft
        fields = '__all__'
        # read_only_fields = ['auction']
        
        
class MakerAuctionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakerAuction
        fields = ['id', 'auction', 'status']
        read_only_fields = ['status']        