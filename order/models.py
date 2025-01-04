from django.db import models

from customers.models import Customer
from handcrafts.models import Handcraft

# Create your models here.
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.PROTECT)
    total_price = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    delivery = models.BooleanField()
    location = models.TextField(null= True , blank=True)
    latitude = models.FloatField(null= True , blank=True)
    longitude = models.FloatField(null= True , blank=True)
    cost = models.IntegerField(null= True , blank=True, default=0)
    customer_phone = models.CharField(max_length = 50,null= True , blank=True)


class OrderHandcraft(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    handcraft = models.ForeignKey(Handcraft, on_delete = models.PROTECT)
    quantity = models.IntegerField()
    price = models.IntegerField()

