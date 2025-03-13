from django.urls import path
from .views import generate_image

urlpatterns = [
    path('sofaPillowImage/',generate_image),
]