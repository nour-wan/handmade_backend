from django.shortcuts import render
from rest_framework.response import Response

from customers.models import Customer
from handcrafts.models import Handcraft
from users.permissions import IsAdminUser, IsCustomerUser
from .serializer import OrderSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password
from .models import Order,OrderHandcraft
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import datetime
from django.db import transaction

from discount.models import Discount, DiscountHandcraft

import logging

logger = logging.getLogger(__name__)

# Create your views here.
class OrderForAdmin(APIView):
    permission_classes = [IsAdminUser] 
    def get(self, request):
        orders = Order.objects.all()
        data = []
        for order in orders:
            serializer = OrderSerializer(order)
            data.append(serializer.data) 
        # serializer = OrderSerializer(orders, many=True)
        return Response({
                'message' : 'get successfully',
                'data' : data
            },status=status.HTTP_200_OK)
    
    
class OrderForCustomer(APIView):  
    permission_classes = [IsCustomerUser] 
    
    def post(self, request):
        try:
            user = request.user 
            customer = user.customer
            customer_id = customer.id
            customer_phone = request.data.get('customer_phone')
            date_of_order = datetime.date.today()
            time_of_order = datetime.datetime.now().time()
            full_price = 0
            # full_cost = 0
            handcraft=  request.data.get('handcraft')

            if not customer_phone or not handcraft :
                return Response({
                    'message' : 'missing fields',
                    'data' : {}
                },status=status.HTTP_404_NOT_FOUND)

            try:
                customer1 = Customer.objects.get(id = customer_id)
            except Customer.DoesNotExist:
                return Response({
                    'message' : 'missing customer',
                    'data' : {}
                },status=status.HTTP_404_NOT_FOUND)
            try :
                with transaction.atomic():
                    order = Order.objects.create(
                        customer = customer1,
                        date_of_order = date_of_order,
                        time_of_order = time_of_order,
                        customer_phone=customer_phone,
                    )
                    if customer_phone:
                        order.customer_phone = customer_phone
                        order.save()
                    handcraft_order = []



                    if handcraft:
                        for hc in handcraft:
                            handcrafts = hc.get('handcraft_id')
                            quantity = hc.get('quantity')

                            try :
                                find_handcraft = Handcraft.objects.get(id = handcrafts)

                            except Handcraft.DoesNotExist:
                                raise Handcraft.DoesNotExist('missing handcraft')
                            if find_handcraft.handcraft_count - quantity < 0 :
                                raise ValueError('the quantity is more than what you have')

                            find_handcraft.handcraft_count = find_handcraft.handcraft_count - quantity
                            find_handcraft.save()
                            
                            if find_handcraft.handcraft_price is not None:
                                price_discount=find_handcraft.handcraft_price 
                                find_price_discount=DiscountHandcraft.objects.filter(handcraft=find_handcraft).first()
                                if find_price_discount : 
                                    d=Discount.objects.filter(id=find_price_discount.discount)
                                    print("Discount object")
                                    print(d)
                                    print("price_discount")
                                    print(price_discount)
                                    price_discount=price_discount * (d.precentage/100)
                                    print(price_discount)
                                order_handcraft = OrderHandcraft.objects.create(
                                   order = order,
                                   handcraft = find_handcraft,
                                  quantity = quantity,
                                   price = price_discount
                                )
                                handcraft_order.append(order_handcraft)
                            
                                full_price = full_price + (quantity*find_handcraft.handcraft_price)
                                # full_cost = full_cost + (quantity*find_handcraft.handcraft_cost)
                            else:
                                raise ValueError(f"Handcraft cost for {find_handcraft.id} is not set.")

                        order.full_price = full_price
                        # order.full_cost = full_cost
                        order.save()



                transaction.commit()    
                return Response({
                        'message' : 'order was added successfully',
                        'data' :  { }   ,   
                    },status=status.HTTP_200_OK)
            except (Handcraft.DoesNotExist, ValueError, 
                    Discount.DoesNotExist) as e :
                transaction.rollback()      
                return Response({
                    'message' : str(e),
                    'data' : {}
                },status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            loggera=logger.exception("An error occurred: %s", str(e))
            return Response({
                'message': 'An unexpected error occurred',
                'data': {loggera}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
     
    def get(self, request):
        user = request.user 
        customer = user.customer
        customer_id = customer.id
        customer1 = Customer.objects.get(id = customer_id)
        orders = Order.objects.filter(customer=customer1)
        data = []
        for order in orders:
            serializer = OrderSerializer(order)
            data.append(serializer.data) 
        # serializer = OrderSerializer(orders, many=True)
        return Response({
                'message' : 'orders get successfully',
                'data' : data
            },status=status.HTTP_200_OK)    





    
# class OrderCustomerDetail(APIView):
#     permission_classes = [IsCustomerUser] 

#     def put(self, request, pk):
#         user = request.user 
#         customer = user.customer
#         customer_id = customer.id
#         customer1 = Customer.objects.get(id = customer_id)
#         orders = Order.objects.filter(customer=customer1)
#         try:
#             order = Order.objects.get(id = pk)
#             return Response({
#                 'message' : 'order was edited successfully',
#                 'data' : {}
#             },status=status.HTTP_200_OK)
#         except Patron.DoesNotExist:
#             return Response({
#                 'message' : 'order not be found',
#                 'data' : {}
#             },status=status.HTTP_404_NOT_FOUND)
        
#     def delete(self, request , pk): 
#         return Response({
#                 'message' : 'cannot delete order',
#                 'data' : {}
#             },status=status.HTTP_403_FORBIDDEN)


# class MyOrder(APIView):
#     # permission_classes = [IsAuthenticated]  
#     def get(self, request, pk):
#         try:
#             custom = Customer.objects.get(id = pk)
#             orders = Order.objects.filter(customer_id = pk)
#             data = []
#             for order in orders:
#                 serializer = OrderSerializer.to_array(order,Design.objects.filter(order = order.id))
#                 data.append(serializer) 
#             # serializer = OrderSerializer(orders, many=True)
#             return Response({
#                     'message' : 'get successfully',
#                     'data' : data
#                 },status=status.HTTP_200_OK)
#         except Customer.DoesNotExist:
#             return Response({
#                 'message' : 'customer not be found',
#                 'data' : {}
#             },status=status.HTTP_404_NOT_FOUND)






