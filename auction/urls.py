from django.urls import path, include


from .views import AuctionDetail, AuctionHandcraftCreateView, AuctionList, AuctionMakerDetail,AuctionHandcraftDetail, AuctionPost, MakerAuctionRequestView, ManageMakerAuctionView

urlpatterns = [
    path('', AuctionList.as_view()),  
    path('add', AuctionPost.as_view()), 
    path('<int:pk>', AuctionDetail.as_view()), 
    path('makers/auction_id/<int:pk>', AuctionMakerDetail.as_view()), 
    path('handcrafts/auction_id/<int:pk>', AuctionHandcraftDetail.as_view()),
    path('auction-requests', MakerAuctionRequestView.as_view()),
    path('manage-auction-requests', ManageMakerAuctionView.as_view()),
    path('manage-auction-requests/<int:pk>', ManageMakerAuctionView.as_view()),
    path('auction-handcrafts', AuctionHandcraftCreateView.as_view()),
]
# router = DefaultRouter()
# router.register(r'auctions', AuctionViewSet, basename='auction')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('auctions/<int:pk>/makers/', AuctionViewSet.as_view({'get': 'get_makers'}), name='get_makers'),
#     path('auctions/<int:pk>/handicrafts/', AuctionViewSet.as_view({'get': 'get_handicrafts'}), name='get_handicrafts'),


# ]

