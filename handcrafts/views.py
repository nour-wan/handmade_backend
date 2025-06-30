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
            serializer.save(maker=maker)    
            # Handcraft.objects.filter(id=serializer.instance.id).update(maker_id=maker_id)   
            category= serializer.instance.category
            allow_simulation= category.allow_simulation if hasattr(category,'allow_simulation') else False    
            return Response({
                'message' : 'Handcraft was added successfully',
                'data' : serializer.data,
                'allow_simulation' : allow_simulation
            },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'errors': serializer.errors
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
            user = request.user
            maker = None
            if hasattr(user, 'maker'): 
                maker = user.maker
            print(request.data)
            handcraft = Handcraft.objects.get(id = pk)
            handcraft_name = request.data.get('handcraft_name')
            handcraft_price = request.data.get('handcraft_price')
            handcraft_image  = request.FILES.get('handcraft_image')
            handcraft_count = request.data.get('handcraft_count')
            if handcraft.maker is None and maker:
                handcraft.maker = maker
            if handcraft_name:
                handcraft.handcraft_name = handcraft_name
            if handcraft_price:
                handcraft.handcraft_price = handcraft_price
            if handcraft_image:
                handcraft.handcraft_image = handcraft_image
            if handcraft_count:
                handcraft.handcraft_count = handcraft_count
                
            category = handcraft.category
            allow_simulation= request.data.get('allow_simulation')
            if allow_simulation is not None : 
                if category.allow_simulation != allow_simulation:
                    category.allow_simulation = allow_simulation    
                    category.save()
        
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
        except Exception as e: # إضافة معالجة عامة للأخطاء
            return Response({
                'message': str(e),
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)           

    def delete(self, request, pk):
            return Response({
                'message' : 'cannot delete Handcraft',
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
        data_with_simulation = []
        for item in serializer.data:
            handcraft_obj = handcraft.get(id=item['id'])
            allow_simulation = handcraft_obj.category.allow_simulation if hasattr(handcraft_obj.category, 'allow_simulation') else False
            item['allow_simulation'] = allow_simulation
            data_with_simulation.append(item)
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
            serializer = HandcraftWithDiscountSerializer(handcraft,many=True)
            data_with_simulation = []
            for item in serializer.data:
                handcraft_obj = handcraft.get(id=item['id'])
                allow_simulation = handcraft_obj.category.allow_simulation if hasattr(handcraft_obj.category, 'allow_simulation') else False
                item['allow_simulation'] = allow_simulation
                data_with_simulation.append(item)
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