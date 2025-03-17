from django.shortcuts import render
from rest_framework import generics ,permissions
from users.serializer import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from .serializer import HandcraftSerializer, HandcraftWithDiscountSerializer
from .models import Handcraft
from users.permissions import IsCustomerUser, IsMakerUser, IsAllUser
# Create your views here.


class HandcraftList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]   
    serialzer_class=UserSerializer 
                
    def get(self,request):
        user = request.user 
        maker = user.maker
        maker_id = maker.id
        print("makerId is ####")
        print(maker_id)
        handcraft=Handcraft.objects.filter(maker_id = maker_id)
        serializer = HandcraftSerializer(handcraft,many=True)
        # print(categories)
        return Response({
            'message' : 'handcraft get successfully',
            "data":serializer.data
            },status=status.HTTP_200_OK)
    
    def post(self,request):
        user = request.user 
        maker = user.maker
        maker_id = maker.id
        serializer = HandcraftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()    
            Handcraft.objects.filter(id=serializer.instance.id).update(maker_id=maker_id)       
            return Response({
                'message' : 'Handcraft was added successfully',
                'data' : {}
            },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)
               
 
          
class HandcraftDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]   
    serialzer_class=UserSerializer

    def get(self, request , pk):
        try:
            handcraft = Handcraft.objects.get(id = pk)
            serializer = HandcraftSerializer(handcraft)
            return Response({
                'message' : 'Handcraft was get successfully',
                'data' :  serializer.data
            },status=status.HTTP_200_OK)
        except Handcraft.DoesNotExist:
            return Response({
                'message' : 'Handcraft not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
            
    def put(self, request, pk):
        try:
            print(request.data)
            handcraft = Handcraft.objects.get(id = pk)
            handcraft_name = request.data.get('handcraft_name')
            handcraft_price = request.data.get('handcraft_price')
            handcraft_image  = request.FILES.get('handcraft_image')
            handcraft_count = request.data.get('handcraft_count')

            if handcraft_name:
                handcraft.handcraft_name = handcraft_name
            if handcraft_price:
                handcraft.handcraft_price = handcraft_price
            if handcraft_image:
                handcraft.handcraft_image = handcraft_image
            if handcraft_count:
                handcraft.handcraft_count = handcraft_count
        
            handcraft.save()
            serializer = HandcraftSerializer(handcraft).data
            return Response({
                'message' : ' handcraft was updated successfully ',
                'data' : serializer
            },status=status.HTTP_200_OK)
        except Handcraft.DoesNotExist:
            return Response({
                'message' : 'Handcraft not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)       

    def delete(self, request, pk):
            return Response({
                'message' : 'can not delete Handcraft',
                'data' : {}
            },status=status.HTTP_200_OK)
        # try:
        #     handcraft = Handcraft.objects.get(id = pk)
        #     handcraft.delete()
        #     return Response({
        #         'message' : 'Handcraft was deleted successfully',
        #         'data' : {}
        #     },status=status.HTTP_200_OK)
        # except Handcraft.DoesNotExist:
        #     return Response({
        #         'message' : 'Handcraft not be found',
        #         'data' : {}
        #     },status=status.HTTP_404_NOT_FOUND)
            
    
class AllHandcraftList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsAllUser]
    serialzer_class=HandcraftWithDiscountSerializer 
                
    def get(self,request):
        handcraft=Handcraft.objects.all()
        serializer = HandcraftWithDiscountSerializer(handcraft,many=True)
        # print(categories)
        return Response({
            'message' : 'handcraft get successfully',
            "data":serializer.data
            },status=status.HTTP_200_OK)    
       
        
class HandcraftByCategoryList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsAllUser]
    serialzer_class=UserSerializer   
    
    def get(self, request , pk):
        try:
            handcraft = Handcraft.objects.filter(category_id = pk)
            serializer = HandcraftSerializer(handcraft,many=True)
            return Response({
                'message' : 'Handcraft was get successfully',
                'data' :  serializer.data
            },status=status.HTTP_200_OK)
        except Handcraft.DoesNotExist:
            return Response({
                'message' : 'Handcraft not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)     
            
            
          
class HandcraftDetailById(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated&IsCustomerUser]   
    serialzer_class=UserSerializer

    def get(self, request , pk):
        try:
            handcraft = Handcraft.objects.get(id = pk)
            serializer = HandcraftWithDiscountSerializer(handcraft)
            return Response({
                'message' : 'Handcraft was get successfully',
                'data' :  serializer.data
            },status=status.HTTP_200_OK)
        except Handcraft.DoesNotExist:
            return Response({
                'message' : 'Handcraft not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)           