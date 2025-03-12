from django.urls import path
from .views import ProcessImagesView

urlpatterns = [
    path('process-images/', ProcessImagesView.as_view(), name='process-images'),
]