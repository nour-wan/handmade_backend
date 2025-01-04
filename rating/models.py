from django.db import models

from customers.models import Customer
from handcrafts.models import Handcraft


# Create your models here.

class Rating(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE,blank=True, null=True)
    handcraft = models.ForeignKey(Handcraft, on_delete = models.CASCADE)
    stars = models.FloatField()