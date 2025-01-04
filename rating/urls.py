from django.urls import path
from . import views
urlpatterns = [
    path('',views.RatingList.as_view()),
    path('<int:pk>',views.RatingDetail.as_view()),
    path('handcraft/<int:pk>',views.RatingByHandcraftsDetail.as_view()),
]