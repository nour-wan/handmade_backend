from django.shortcuts import render
from rest_framework.response import Response
from .serializer import OrderSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password
from .models import Order,OrderClothes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import datetime
from django.db import transaction

from discount.models import Discount



# Create your views here.
class OrderList(APIView):
    # permission_classes = [IsAuthenticated] 
    def get(self, request):
        orders = Order.objects.all()
        data = []
        for order in orders:
            serializer = OrderSerializer.to_array(order,Design.objects.filter(order = order.id))
            data.append(serializer) 
        # serializer = OrderSerializer(orders, many=True)
        return Response({
                'message' : 'get successfully',
                'data' : data
            },status=status.HTTP_200_OK)
    
    def post(self, request):
        customer = request.data.get('customer')
        delivery = request.data.get('delivery')
        location = request.data.get('location')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        clothes = request.data.get('clothes')
        design = request.data.get('design')
        customer_phone = request.data.get('customer_phone')
        date = datetime.date.today()
        time = datetime.datetime.now().time()
        total_price = 0
        total_cost = 0
        if not customer and not delivery :
            return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
        if  not clothes and not design:
            return Response({
                'message' : 'cannot create order',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
        

        try:
            customer1 = Customer.objects.get(id = customer)
        except Customer.DoesNotExist:
            return Response({
                'message' : 'missing customer',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
        try :
            with transaction.atomic():
                order = Order.objects.create(
                    customer = customer1,
                    total_price = total_price,
                    date = date,
                    time = time,
                    delivery = delivery
                )
                if customer_phone:
                    order.customer_phone = customer_phone
                    order.save()
                clothes_order = []
                design_order = []
                patron_order = []
                fabric_order = []
                photo_order = []
                
                if delivery:
                    if location:
                        order.location = location
                    if latitude:
                        order.latitude = latitude 
                    if longitude:
                        order.longitude = longitude
                    order.save()

                
                if clothes:
                    for clothe in clothes:
                        clothess = clothe.get('clothes')
                        quantity = clothe.get('quantity')
                        # price = clothe.get('price')

                        try :
                            find_clothes = Clothes.objects.get(id = clothess)
                            
                        except Clothes.DoesNotExist:
                            raise Clothes.DoesNotExist('missing clothes')
                            # transaction.rollback()
                            # return Response({
                            #     'message' : 'missing clothes',
                            #     'data' : {}
                            # },status=status.HTTP_404_NOT_FOUND)
                        if find_clothes.count - quantity < 0 :
                            raise ValueError('the quantity is more than what you have')
                            # transaction.rollback()
                            # return Response({
                            #     'message' : 'the quantity is more than what you have',
                            #     'data' : {}
                            # },status=status.HTTP_404_NOT_FOUND)
                        find_clothes.count = find_clothes.count - quantity
                        find_clothes.save()
                        order_clothes = OrderClothes.objects.create(
                            order = order,
                            clothes = find_clothes,
                            quantity = quantity,
                            price = find_clothes.price
                        )
                        clothes_order.append(order_clothes)
                        total_price = total_price + (quantity*find_clothes.price)
                        total_cost = total_cost + (quantity*find_clothes.cost)
                    order.total_price = total_price
                    order.cost = total_cost
                    try:
                        discont = Discount.objects.first()
                        print(discont)
                        if discont:
                            order.total_price = order.total_price * discont.precentage
                    except Discount.DoesNotExist:
                        raise Discount.DoesNotExist('missing discount')    
                    order.save()
                if design:
                    for design0 in design:
                        customer_id = design0.get('customer_id')
                        printer_id = design0.get('printer_id')
                        name = design0.get('name')
                        image = design0.get('image')
                        size = design0.get('size')
                        photo_design = design0.get('photo_design')
                        fabrics_design = design0.get('fabrics_design')
                        patron_design = design0.get('patron_design')
                        quantity = design0.get('quantity')
                        if not customer_id or not name or not image or not fabrics_design or not patron_design:
                            raise ValueError('missing fields')
                            # return Response({
                            #     'message' : 'missing fields',
                            #     'data' : {}
                            # },status=status.HTTP_404_NOT_FOUND)
                        if customer_id != customer:
                            raise ValueError('cannot find customer')
                        
                        create_design = Design.objects.create(
                            order = order,
                            customer = customer1,
                            name = name,
                            image = image,
                            status = "not accept"
                        )
                        design_order.append(create_design)
                        if quantity:
                            create_design.quantity = quantity
                            create_design.save()
                        if printer_id:
                            try :
                                find_printer = Printers.objects.get(id = printer_id)
                                create_design.printer = find_printer
                                create_design.save()
                            except Printers.DoesNotExist:
                                raise Printers.DoesNotExist('cannot find printer')
                        if size:
                            create_design.size = size
                            create_design.save()
                        if photo_design:
                            for photo0 in photo_design:
                                photo_id = photo0
                                try:
                                    get_photo = Photo.objects.get(id = photo_id)
                                    create_photo_design = PhotoDesign.objects.create(
                                        photo = get_photo, 
                                        design = create_design
                                    )
                                    photo_order.append(create_photo_design)
                                except Photo.DoesNotExist:
                                    raise Photo.DoesNotExist('cannot find photo')
                        if fabrics_design:
                            for fabric0 in fabrics_design:
                                fabric_id = fabric0
                                try:
                                    get_fabric = Fabrics.objects.get(id = fabric_id) 
                                    create_fabric_design = FabricsDesign.objects.create(
                                        fabrics = get_fabric,
                                        design = create_design
                                    )
                                    fabric_order.append(create_fabric_design)
                                except Fabrics.DoesNotExist:
                                    raise Fabrics.DoesNotExist('cannot find fabric') 
                        
                        if patron_design:
                            for patron in patron_design:
                                patron_id = patron.get("patron_id") 
                                width = patron.get("width")  
                                height = patron.get("height") 
                                try:
                                    get_patron = Patron.objects.get(id = patron_id)
                                    create_patron_design = PatronDesign.objects.create(
                                        patron = get_patron,
                                        design = create_design,
                                        width = width,
                                        height = height
                                    )  
                                    patron_order.append(create_patron_design)
                                except Patron.DoesNotExist:
                                    raise Patron.DoesNotExist('cannot find patron') 


            transaction.commit()    
            serializer = OrderSerializer.to_array(order,design_order)
            return Response({
                    'message' : 'order was added successfully',
                    'data' : 
                        serializer,      
                },status=status.HTTP_200_OK)
        except (Clothes.DoesNotExist, ValueError, Printers.DoesNotExist, Photo.DoesNotExist, Fabrics.DoesNotExist, Patron.DoesNotExist, Discount.DoesNotExist) as e :
            transaction.rollback()      
            return Response({
                'message' : str(e),
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
        




        



        











            # return Response({'me':True})
        return Response({'me':False})


class OrderDetail(APIView):
    # permission_classes = [IsAuthenticated] 

    def get(self, request , pk):
        try:
            order = Order.objects.get(id = pk)
            return Response({
                'message' : 'order was get successfully',
                'data' :  OrderSerializer.to_array(order,Design.objects.filter(order = order.id))
            },status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({
                'message' : 'order not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            order = Order.objects.get(id = pk)
            return Response({
                'message' : 'order was edited successfully',
                'data' : {}
            },status=status.HTTP_200_OK)
        except Patron.DoesNotExist:
            return Response({
                'message' : 'order not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request , pk): 
        return Response({
                'message' : 'cannot delete order',
                'data' : {}
            },status=status.HTTP_403_FORBIDDEN)


class MyOrder(APIView):
    # permission_classes = [IsAuthenticated]  
    def get(self, request, pk):
        try:
            custom = Customer.objects.get(id = pk)
            orders = Order.objects.filter(customer_id = pk)
            data = []
            for order in orders:
                serializer = OrderSerializer.to_array(order,Design.objects.filter(order = order.id))
                data.append(serializer) 
            # serializer = OrderSerializer(orders, many=True)
            return Response({
                    'message' : 'get successfully',
                    'data' : data
                },status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({
                'message' : 'customer not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)






