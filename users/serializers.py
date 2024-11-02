# serializers.py
from rest_framework import serializers
from django.core.mail import send_mail
import random
import datetime
from users.models import Users
from users.utils import generate_verification_code, send_verification_email
import pytz
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

    def save(self):
        timezone = pytz.utc
        email = self.validated_data['email']
        code = generate_verification_code() # Generate a 6-digit code
        user = Users.objects.get(email=email)
        user.reset_code = code  # Assuming you've added `reset_code` field to the User profile
        user.code_expiration = datetime.datetime.now(timezone) + datetime.timedelta(minutes=60)  # 10-minute expiration
        user.save()  # Save the code to the user's profile
        send_verification_email(email,code)
        # send_mail(
        #     'Password Reset Code',
        #     f'Your password reset code is: {code}',
        #     'from@example.com',
        #     [email],
        #     fail_silently=False,
        # )
        
        
        
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    # code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = Users.objects.get(email=attrs['email'])
        if not Users.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("No user found with this email.")
        # if user.reset_code != attrs['code']:
        #     raise serializers.ValidationError("Invalid code.")
        return attrs

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = Users.objects.get(email=email)
        user.set_password(new_password)
        user.reset_code = None  # Clear the reset code
        user.code_expiration = None
        user.save()   