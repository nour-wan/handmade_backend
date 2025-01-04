from django.db import models

from customers.models import Customer
from handcrafts.models import Handcraft

# Create your models here.
class Comment(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE,blank=True, null=True)
    handcraft = models.ForeignKey(Handcraft, on_delete = models.CASCADE)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    description = models.CharField(max_length = 500)
