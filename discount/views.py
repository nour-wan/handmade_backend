from rest_framework.response import Response

from maker.models import Maker
from .serializer import DiscountHandcraftSerializer, DiscountSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from .models import Discount, DiscountHandcraft
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsAdminUser, IsCustomerUser, IsMakerUser, IsMakerUserIsCustomerUser
from users.serializer import UserSerializer
from rest_framework import generics ,permissions
# Create your views here.

class DiscountList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]   
    serialzer_class=UserSerializer 
    def get(self, request):
        discount = Discount.objects.all()
        serializer = DiscountSerializer(discount, many=True)
        return Response({
                'message' : 'get successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user 
        maker = user.maker
        maker_id = maker.id
        serializer = DiscountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            Discount.objects.filter(id=serializer.instance.id).update(maker=maker_id) 
            return Response({
                'message' : 'discount was added successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)




class DiscountDetail(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]  
    serialzer_class=UserSerializer 

    def get(self, request , pk):
        try:
            discount = Discount.objects.get(id = pk)
            return Response({
                'message' : 'discount was get successfully',
                'data' : DiscountSerializer(discount).data
            },status=status.HTTP_200_OK)
        except Discount.DoesNotExist:
            return Response({
                'message' : 'discount not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            discount = Discount.objects.get(id = pk)
            name = request.data.get('name')
            precentage = request.data.get('precentage')
            from_date = request.data.get('from_date')
            to_date = request.data.get('to_date')
            if name:
                discount.name = name
            if precentage:
                discount.precentage = precentage
            if from_date:
                discount.from_date = from_date
            if to_date:
                discount.to_date = to_date   
            discount.save()
            serializer = DiscountSerializer(discount)
            return Response({
                'message' : 'discount was edited successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        except Discount.DoesNotExist:
            return Response({
                'message' : 'discount not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
    def delete(self, request , pk):  
        try:
             discount = Discount.objects.get(id = pk)
             discount.delete()
             return Response({
                 'message' : 'discount was deleted successfully',
                 'data' : {}
             },status=status.HTTP_200_OK)
        except Discount.DoesNotExist:
             return Response({
                 'message' : 'discount not be found',
                 'data' : {}
             },status=status.HTTP_404_NOT_FOUND)

    




    
class DiscountListToMaker(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]   
    serializer_class = DiscountSerializer 
    def get(self, request):
        user = request.user 
        maker = user.maker
        maker_id = maker.id
        discount = Discount.objects.filter(maker_id=maker_id)
        serializer = self.serializer_class(discount, many=True)
        if not discount.exists():
            return Response({
                'message': 'No discounts found for this maker.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
                'message' : 'get successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        
        
 

class DiscountHandcraftPost(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]   
    serialzer_class=UserSerializer 
    
    def post(self, request):
        discount = request.data.get("discount")
        handcraft = request.data.get("handcraft")
        if DiscountHandcraft.objects.filter(discount_id=discount,handcraft_id=handcraft) :
            return Response({
                'message' : 'discount handcraft is already exist',
                'data' : []
            },status=status.HTTP_400_BAD_REQUEST)
        serializer = DiscountHandcraftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message' : 'discount handcraft was added successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)

class DiscountHandcraftDelete(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUser]   
    serialzer_class=UserSerializer 
    def delete(self, request,dis,hand): 
        try:
             data=DiscountHandcraft.objects.get(discount_id=dis,handcraft_id=hand)
             data.delete()
             return Response({
                 'message' : 'discount handcraft was deleted successfully',
                 'data' : {}
             },status=status.HTTP_200_OK)
        except DiscountHandcraft.DoesNotExist:
             return Response({
                 'message' : 'discount handcraft not be found',
                 'data' : {}
             },status=status.HTTP_404_NOT_FOUND)
             
            