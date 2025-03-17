from django.urls import path
from . import views


urlpatterns = [
    path('',views.HandcraftList.as_view()),
    path('<int:pk>',views.HandcraftDetail.as_view()),
    path('all-user',views.AllHandcraftList.as_view()),
    path('by-category/<int:pk>',views.HandcraftByCategoryList.as_view()),
    path('detail-by-handcraftId/<int:pk>',views.HandcraftDetailById.as_view()),
] 