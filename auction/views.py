from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from handcrafts.serializer import HandcraftSerializer
from maker.serializer import MakerSerializer, MakerSignupSerializer
from .models import AuctionHandcraft, Maker, Handcraft, Auction, MakerAuction
from .serializers import MakerAuctionRequestSerializer, MakerAuctionSerializer, AuctionHandcraftSerializer, AuctionSerializer
from rest_framework import generics ,permissions
from users.permissions import IsAdminUser, IsAllUser, IsMakerUser
from users.serializer import UserSerializer
from rest_framework import generics ,permissions
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class AuctionList(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsAllUser]   
    serialzer_class=UserSerializer 
    def get(self, request):
        auction = Auction.objects.all()
        serializer = AuctionSerializer(auction, many=True)
        return Response({
                'message' : 'Auction was get successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        
    
class AuctionPost(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsAdminUser]  
    serialzer_class=UserSerializer 
    def post(self, request):
        serializer = AuctionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message' : 'Auction was added successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        return Response({
                'message' : 'missing fields',
                'data' : {}
            },status=status.HTTP_400_BAD_REQUEST)
        
        
class AuctionDetail(generics.RetrieveAPIView):   
    permission_classes = [permissions.IsAuthenticated&IsAdminUser]  
    serialzer_class=UserSerializer 

    def put(self, request, pk):
        try:
            auction = Auction.objects.get(id = pk)
            name = request.data.get('name')
            location = request.data.get('location')
            from_date = request.data.get('from_date')
            to_date = request.data.get('to_date')
            description = request.data.get('description')
            if name:
                auction.name = name
            if location:
                auction.location = location
            if from_date:
                auction.from_date = from_date
            if to_date:
                auction.to_date = to_date   
            if description:
                auction.description = description 
            auction.save()
            serializer = AuctionSerializer(auction)
            return Response({
                'message' : 'auction was edited successfully',
                'data' : serializer.data
            },status=status.HTTP_200_OK)
        except Auction.DoesNotExist:
            return Response({
                'message' : 'auction not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
            
    def delete(self, request , pk):  
        try:
             auction = Auction.objects.get(id = pk)
             auction.delete()
             return Response({
                 'message' : 'auction was deleted successfully',
                 'data' : {}
             },status=status.HTTP_200_OK)
        except Auction.DoesNotExist:
             return Response({
                 'message' : 'auction not be found',
                 'data' : {}
             },status=status.HTTP_404_NOT_FOUND)
    
class AuctionMakerDetail(APIView):
    permission_classes = [permissions.IsAuthenticated&IsAllUser]   
    serialzer_class=UserSerializer
    def get(self, request , pk):
        try:
            makers = MakerAuction.objects.filter(auction=pk)
            # serializer = MakerAuctionSerializer(makers, many=True)
            
            response_data = []

            for maker in makers:
                auction_serializer = Auction.objects.get(id=maker.auction_id)
                maker_serializer =Maker.objects.get(id=maker.maker_id)
                print("@@@@@@@@@@@@@")
                print(maker_serializer)
                response_data.append(
                    # 'id': maker.id,
                    # 'status': maker.status,
                   MakerSerializer(maker_serializer).data,  # تفاصيل الصانع
                    # 'auction': AuctionSerializer(auction_serializer).data # تفاصيل المزاد
                )
                return Response({
                    'message' : 'Auction makers were get successfully',
                    'data' : response_data
                },status=status.HTTP_200_OK)
            
        except Auction.DoesNotExist:
            return Response({
                'message' : 'Auction not be found',
                'data' : {}
            },status=status.HTTP_404_NOT_FOUND)
    
class AuctionHandcraftDetail(APIView):
    permission_classes = [permissions.IsAuthenticated&IsAllUser]   
    serialzer_class=UserSerializer


    def get(self, request , pk):
            try:
                handcrafts = AuctionHandcraft.objects.filter(auction=pk)
                serializer = AuctionHandcraftSerializer(handcrafts, many=True)
                response_data = []

                for handcraft in handcrafts:
                    auction_serializer = Auction.objects.get(id=handcraft.auction_id)
                    handcraft_serializer =Handcraft.objects.get(id=handcraft.handcraft_id)
                    print("@@@@@@@@@@@@@")
                    print(handcraft_serializer)
                    response_data.append(
                         HandcraftSerializer(handcraft_serializer).data,  # تفاصيل الصانع
                        
                    )
                return Response({
                        'message' : 'Auction handcraft were get successfully',
                        'data' : response_data
                    },status=status.HTTP_200_OK)
    #             return Response({
    #                 'message' : 'Auction handcrafts were get successfully',
    #                 'data' : serializer.data
    
    # },status=status.HTTP_200_OK)
            except Auction.DoesNotExist:
                return Response({
                    'message' : 'Auction not be found',
                    'data' : {}
                },status=status.HTTP_404_NOT_FOUND)
  
  
# طلبات الانضمام للمزاد
class MakerAuctionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated&IsMakerUser] 

    def post(self, request):
        serializer = MakerAuctionRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(maker=request.user.maker, status='pending')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# إدارة الطلبات من قبل الأدمن
class ManageMakerAuctionView(APIView):
    permission_classes = [IsAuthenticated & IsAdminUser]

    def get(self, request):
        requests = MakerAuction.objects.filter(status='pending')
        response_data = []

        for auction_request in requests:
            auction_serializer = Auction.objects.get(id=auction_request.auction_id)
            maker_serializer =Maker.objects.get(id=auction_request.maker_id)
            print("@@@@@@@@@@@@@")
            print(maker_serializer)
            response_data.append({
                'id': auction_request.id,
                'status': auction_request.status,
                'maker': MakerSerializer(maker_serializer).data,  # تفاصيل الصانع
                'auction': AuctionSerializer(auction_serializer).data # تفاصيل المزاد
            })

        return Response(response_data)
        # serializer = MakerAuctionSerializer(requests, many=True)
        # return Response(serializer.data)

    def patch(self, request, pk):
        try:
            auction_request = MakerAuction.objects.get(pk=pk)
            new_status = request.data.get('status')
            
            if new_status in ['approved', 'rejected']:
                auction_request.status = new_status
                auction_request.save()
                return Response({'status': 'updated'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        except MakerAuction.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

# إضافة منتجات للمزاد
class AuctionHandcraftCreateView(APIView):
    permission_classes = [IsAuthenticated & IsMakerUser]

    def post(self, request):
        if not MakerAuction.objects.filter(
            maker=request.user.maker,
            auction_id=request.data.get('auction'),
            status='approved'
        ).exists():
            return Response({'error': 'Not approved for this auction'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AuctionHandcraftSerializer(data=request.data)
        if serializer.is_valid():
            handcraft_instance = serializer.save()

            # جلب تفاصيل المزاد
            auction = handcraft_instance.auction
            auction_serializer = AuctionSerializer(auction)

            # جلب تفاصيل العمل اليدوي
            handcraft_serializer = HandcraftSerializer(handcraft_instance.handcraft)

            # بناء الاستجابة
            response_data = {
                'id': handcraft_instance.id,
                'auction': auction_serializer.data,
                'handcraft': handcraft_serializer.data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    