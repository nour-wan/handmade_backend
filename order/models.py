from django.db import models

from customers.models import Customer
from handcrafts.models import Handcraft

# Create your models here.
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.PROTECT,related_name='orders')
    full_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0) 
    date_of_order = models.DateField()
    time_of_order = models.TimeField()
    delivery = models.BooleanField(default=True)
    customer_phone = models.CharField(max_length = 50,null= True , blank=True)
    # full_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0) 


class OrderHandcraft(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE,related_name='orderhandcrafts')
    handcraft = models.ForeignKey(Handcraft, on_delete = models.PROTECT)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

