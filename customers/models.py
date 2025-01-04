from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Users

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(Users , related_name="customer", on_delete=models.PROTECT)
    # name = models.CharField(max_length = 50 )
    phone_number = models.IntegerField()
   


    def __str__(self):
        return self.user.username
  
    
    