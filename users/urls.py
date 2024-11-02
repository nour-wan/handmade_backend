from django.urls import path
from . import views

urlpatterns = [
    path('email',views.PasswordResetRequestView.as_view()),
    path('code',views.VerifyCodeView.as_view()),
    path('password',views.PasswordResetConfirmView.as_view()),
]