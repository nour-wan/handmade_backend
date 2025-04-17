from rest_framework import serializers

from users.serializer import UserSerializer
from .models import  Maker
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password
from django.contrib import auth
import hashlib
from django.contrib.auth.hashers import check_password
from users.models import Users

class MakerSerializer(serializers.ModelSerializer):
    # user = UserSerializer() 
    
    phone_number = serializers.IntegerField( required=True)
    telegram_id = serializers.CharField( required=True)
    image = serializers.ImageField()
    username = serializers.CharField(source='user.username', read_only=True)  # إضافة حقل username
    email = serializers.EmailField(source='user.email', read_only=True)  # إضافة حقل email

    class Meta:
        model = Maker
        fields = ['phone_number', 'telegram_id', 'image', 'username', 'email'] 
    # class Meta:
    #     model = Users
    #     fields = ['phone_number','telegram_id','image', 'user']
        
        
class MakerSignupSerializer(serializers.ModelSerializer):
    # name = serializers.CharField( required=True)
    phone_number = serializers.IntegerField( required=True)
    telegram_id = serializers.CharField( required=True)
    image = serializers.ImageField()

    class Meta:
        model = Users
        fields = [ 'username' , 'email', 'password','phone_number','telegram_id','image']
        extra_kwargs={
            'password':{'write_only':True}
        } 
        
    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value    
        
    def save(self, **kwargs):
        user=Users(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        password=self.validated_data['password']
        # self.validated_data.setdefault('is_superuser', False)
        user.set_password(password)
        user.is_maker=True
        user.save()
        Maker.objects.create(
            user=user,
            # name=self.validated_data['name'],
            phone_number =self.validated_data['phone_number'],
            telegram_id = self.validated_data['telegram_id'],
            image= self.validated_data['image'],
        )
        return user   
