from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from customers.models import Customer
from handcrafts.models import Handcraft
from .serializer import CommentSerializer
import datetime
from .models import Comment
import jwt
from users.permissions import IsAdminUser, IsCustomerUser, IsMakerUser, IsMakerUserIsCustomerUser
from users.serializer import UserSerializer
from rest_framework import generics ,permissions
# Create your views here.


class CommentList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUserIsCustomerUser]   
    serialzer_class=UserSerializer 
    def get(self, request):
        comment = Comment.objects.all()
        serializer = CommentSerializer.to_array(comment)
        return Response({
                'message' : 'get successfully',
                'data' : serializer
            },status=status.HTTP_200_OK)
    
    def post(self, request):
        # payload = jwt.decode(access_token, options={"verify_signature": False})
        # user_id = payload.get('sub')
        # print(user_id)
        user = request.user 
        customer = user.customer
        customer_id = customer.id
        handcraft = request.data.get('handcraft')
        description = request.data.get('description')
        # serializer = CommentSerializer(data=request.data)
        if   handcraft and  description:
            date = datetime.date.today()
            time = datetime.datetime.now().time()
            try:
                customer1 = Customer.objects.get(id = customer_id)
            except Customer.DoesNotExist:
                return Response({
                'message' : 'cannot find customer',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
                # raise Customer.DoesNotExist('cannot find customer')    
            try:
                handcraft1 = Handcraft.objects.get(id = handcraft)
            except Handcraft.DoesNotExist:
                return Response({
                'message' : 'cannot find clothes',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
                # raise Clothes.DoesNotExist('cannot find clothes')    
            comment = Comment.objects.create(
                 customer = customer1,
                 handcraft = handcraft1,
                 description = description,
                 date = date,
                 time = time
            )
            # serializer.save()
            serializer = CommentSerializer.get_comment(comment)
            return Response({
                    'message' : 'comment was added successfully',
                    'data' : serializer
                },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)

class CommentDetail(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUserIsCustomerUser]   
    serialzer_class=UserSerializer 
    def get(self, request , pk):
        try:
            comment = Comment.objects.get(id = pk)
            serializer = CommentSerializer.get_comment(comment)
            return Response({
                'message' : 'comment was get successfully',
                'data' :  serializer
            },status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({
                'message' : 'comment not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)


    def put(self, request, pk):
        try:
            comment = Comment.objects.get(id = pk)
            description = request.data.get('description')
            if description:
                comment.description = description
                comment.save()
                return Response({
                    'message' : 'comment was edited successfully',
                    'data' : CommentSerializer.get_comment(comment)
                },status=status.HTTP_200_OK)
            return Response({
                    'message' : 'cannot find description',
                    'data' : {}
                },status=status.HTTP_404_NOT_FOUND) 
        except Comment.DoesNotExist:
            return Response({
                'message' : 'comment not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
    def delete(self, request , pk):
        try:
            comment = Comment.objects.get(id = pk)
            comment.delete()
            return Response({
                'message' : 'comment was deleted successfully',
                'data' : {}
            },status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({
                'message' : 'comment not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)


class CommentByHandcraftDetail(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUserIsCustomerUser]   
    serialzer_class=UserSerializer 
    def get(self, request , pk):
        try:
            comment = Comment.objects.filter(handcraft_id = pk)
            serializer = CommentSerializer.to_array(comment)
            return Response({
                'message' : 'comment was get successfully',
                'data' :  serializer
            },status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({
                'message' : 'comment not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
