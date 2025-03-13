from rest_framework import serializers
from .models import Admin
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password
from django.contrib import auth
import hashlib
from django.contrib.auth.hashers import check_password
from users.models import Users

class AdminSignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.IntegerField( required=True)
    telegram_id = serializers.CharField( required=True)
    company_name= serializers.CharField( required=True)

    class Meta:
        model = Users
        fields = [ 'username' , 'email', 'password','phone_number','telegram_id','company_name']
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
        user.is_admin=True
        user.save()
        Admin.objects.create(
            user=user,
           
            phone_number =self.validated_data['phone_number'],
            telegram_id = self.validated_data['telegram_id'],
            company_name= self.validated_data['company_name'],
        )
        return user   
