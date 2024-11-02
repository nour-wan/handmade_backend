from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver

# Create your models here.
class Users(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_maker = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    email = models.EmailField(unique=True)  
    reset_code = models.IntegerField(null=True, blank=True) 
    code_expiration  = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
   
@receiver(post_save , sender=settings.AUTH_USER_MODEL)    
def create_auth_token(sender , instance=None , created=False ,  **kwargs):
    if created:
        Token.objects.create(user=instance)
        
         
    