from django.urls import path
from . import views
urlpatterns = [
    # path('', views.test)
    path('',views.OrderForAdmin.as_view()),
    path('for_customer',views.OrderForCustomer.as_view()),
    
    # path('<int:pk>',views.OrderDetail.as_view()),
    # path('myorder/<int:pk>',views.MyOrder.as_view()),
]