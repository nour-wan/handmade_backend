from django.urls import path
from . import views
urlpatterns = [
    path('',views.CommentList.as_view()),
    path('<int:pk>',views.CommentDetail.as_view()),
    path('handcraft/<int:pk>',views.CommentByHandcraftDetail.as_view()),
]