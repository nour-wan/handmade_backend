from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Users

# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField(Users , related_name="admin", on_delete=models.PROTECT)
    phone_number = models.CharField( max_length = 50)
    telegram_id = models.CharField( max_length = 50)
    company_name = models.CharField(max_length = 50)


    def __str__(self):
        return self.user.username
  
    
    