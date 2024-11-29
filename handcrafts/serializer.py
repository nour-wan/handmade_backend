from rest_framework import serializers
from .models import Handcraft

class HandcraftSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Handcraft
        fields = "__all__"