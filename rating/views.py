from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from handcrafts.models import Handcraft
from .serializer import RatingSerializer
import datetime
from .models import Rating
from users.permissions import IsAdminUser, IsCustomerUser, IsMakerUser, IsMakerUserIsCustomerUser
from users.serializer import UserSerializer
from rest_framework import generics ,permissions

# Create your views here.

class RatingList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsCustomerUser]   
    serialzer_class=UserSerializer 
    def get(self, request):
        rating = Rating.objects.all()
        serializer = RatingSerializer(rating, many= True)
        return Response({
                'message' : 'get successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user 
        customer = user.customer
        customer_id = customer.id
        
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            Rating.objects.filter(id=serializer.instance.id).update(customer_id=customer_id)       
            return Response({
                'message' : 'rating was added successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)



class RatingDetail(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsCustomerUser]   
    serialzer_class=UserSerializer 
    def get(self, request , pk):
        try:
            rating = Rating.objects.get(id = pk)
            serializer = RatingSerializer(rating)
            return Response({
                'message' : 'rating was get successfully',
                'data' :  serializer.data
            },status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            return Response({
                'message' : 'rating not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            rating = Rating.objects.get(id = pk)
            stars = request.data.get('stars')
            if stars:
                rating.stars = stars
                rating.save()
                return Response({
                    'message' : 'rating was edited successfully',
                    'data' : RatingSerializer(rating).data
                },status=status.HTTP_200_OK)
            return Response({
                    'message' : 'cannot find stars',
                    'data' : {}
                },status=status.HTTP_404_NOT_FOUND) 
        except Rating.DoesNotExist:
            return Response({
                'message' : 'rating not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
    def delete(self, request , pk):
        try:
            rating = Rating.objects.get(id = pk)
            rating.delete()
            return Response({
                'message' : 'rating was deleted successfully',
                'data' : {}
            },status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            return Response({
                'message' : 'rating not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)




class RatingByHandcraftsDetail(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsCustomerUser]   
    serialzer_class=UserSerializer 
    def get(self, request , pk):
        try:
            rating = Rating.objects.filter(handcraft_id = pk)
            total = RatingSerializer.rating_by_handcraft(rating)
            return Response({
                'message' : 'rating was get successfully',
                'data' :  total
            },status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            return Response({
                'message' : 'rating not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
