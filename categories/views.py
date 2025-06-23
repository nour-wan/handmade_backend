from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
# from general_information.models import GeneralInformation
from categories.models import Category
from users.permissions import IsAdminUser, IsCustomerUser, IsMakerUser, IsMakerUserIsCustomerUser
from users.serializer import UserSerializer
from .serializer import CategorySerializer
from rest_framework import status
from rest_framework import generics ,permissions
# Create your views here.

            
class CategoryList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsAdminUser]   
    serialzer_class=UserSerializer 
                
    def get(self,request):
        categories=Category.objects.all()
        serializer = CategorySerializer(categories,many=True)
        # print(categories)
        return Response({
            'message' : 'categories get successfully',
            "data":serializer.data
            },status=status.HTTP_200_OK)
    
    def post(self,request):
        try:
            category_name = request.data.get("category_name")
            category_description = request.data.get("category_description")
            category_image= request.data.get("category_image")
            allow_simulation=request.data.get("allow_simulation")
            if allow_simulation not in [True,False]:
                return Response({
                    'message' : 'allow_simulation must be a boolean value (True,False)',
                    'data' : []
                },status=status.HTTP_400_BAD_REQUEST)
            if Category.objects.filter(category_name=category_name) :
                return Response({
                    'message' : 'Category is already exist',
                    'data' : []
                },status=status.HTTP_400_BAD_REQUEST)
            
            Category=Category.object.create(
                category_name=category_name,
                category_description=category_description,
                category_image=category_image,
            allow_simulation= allow_simulation
                
            )    
            serializer = CategorySerializer(Category).data

            if serializer.is_valid():
                # serializer.save()           
                return Response({
                    'message' : 'Category was added successfully',
                    'data' :serializer
                },status=status.HTTP_200_OK)
        except Exception as e :        
            return Response({
                    'message' : str(e),
                    'data' : {}
                },status=status.HTTP_400_BAD_REQUEST)
               
 
          
class CategoryDetail(APIView):
    permission_classes = [permissions.IsAuthenticated&IsAdminUser]   
    serialzer_class=UserSerializer

    def get(self, request , pk):
        try:
            category = Category.objects.get(id = pk)
            serializer = CategorySerializer(category)
            return Response({
                'message' : 'Category was get successfully',
                'data' :  serializer.data
            },status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({
                'message' : 'Category not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
            
    def put(self, request, pk):
        try:
            print(request.data)
            category = Category.objects.get(id = pk)
            category_name = request.data.get('category_name')
            category_description = request.data.get('category_description')
            categorye_image  = request.FILES.get('categorye_image')
            allow_simulation = request.data.get('allow_simulation')

            if category_name:
                category.category_name = category_name
            if category_description:
                category.category_description = category_description
            if categorye_image:
                category.categorye_image = categorye_image
            if allow_simulation is not None:
                category.allow_simulation = allow_simulation    

            category.save()
            serializer = CategorySerializer(category).data
            return Response({
                'message' : ' category was updated successfully ',
                'data' : serializer
            },status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({
                'message' : 'category not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)       

    # def delete(request,category,pk):
    #     try:
    #         category = Category.objects.get(id = pk)
    #         category.delete()
    #         return Response({
    #             'message' : 'category was deleted successfully',
    #             'data' : {}
    #         },status=status.HTTP_200_OK)
    #     except Category.DoesNotExist:
    #         return Response({
    #             'message' : 'subject not be found',
    #             'data' : {}
    #         },status=status.HTTP_404_NOT_FOUND)
            
            
                     
           
class CategoryForMaker(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsMakerUserIsCustomerUser]   
    serialzer_class=UserSerializer 
                
    def get(self,request):
        categories=Category.objects.all()
        serializer = CategorySerializer(categories,many=True)
        # print(categories)
        return Response({
            'message' : 'categories get successfully',
            "data":serializer.data
            },status=status.HTTP_200_OK)            
  