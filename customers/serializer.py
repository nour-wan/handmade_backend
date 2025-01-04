from rest_framework import serializers
from .models import  Customer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password
from django.contrib import auth
import hashlib
from django.contrib.auth.hashers import check_password
from users.models import Users

class CustomerSignupSerializer(serializers.ModelSerializer):
    # name = serializers.CharField( required=True)
    phone_number = serializers.IntegerField( required=True)

    class Meta:
        model = Users
        fields = [ 'username' , 'email', 'password','phone_number']
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
        user.is_customer=True
        user.save()
        Customer.objects.create(
            user=user,
            # name=self.validated_data['name'],
            phone_number =self.validated_data['phone_number'],
        )
        return user   
