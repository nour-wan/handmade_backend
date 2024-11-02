from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import datetime
from .models import Users
from .serializers import PasswordResetRequestSerializer,PasswordResetConfirmSerializer
from rest_framework import status
import pytz
# Create your views here.
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
                'message' : 'Verification code sent , check your email.',
                'data' : {}
            },status=status.HTTP_200_OK)
        
class VerifyCodeView(generics.GenericAPIView):
    # serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        submitted_code = request.data.get('code')

        try:
            user = Users.objects.get(email=email)
            print("here")
            timezone = pytz.utc
            now =  datetime.datetime.now(timezone)
            if (user.reset_code == submitted_code and
                user.code_expiration > now):
                return Response({
                    'message' : 'Code verified. You can now set a new password.',
                    'data' : {}
                },status=status.HTTP_200_OK)
            else:
                return  Response({
                'message' : 'Invalid or expired code',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return Response({
                'message' : 'Email not found..',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
               
               
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
                    'message' : 'Password has been reset.',
                    'data' : {}
                },status=status.HTTP_200_OK)
     
               