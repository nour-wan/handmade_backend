from django.db import models

from handcrafts.models import Handcraft
from maker.models import Maker

# Create your models here.
class Discount(models.Model):
    maker = models.ForeignKey(Maker, on_delete = models.CASCADE,blank=True, null=True)
    name = models.CharField(max_length = 50)
    precentage = models.FloatField()
    from_date =models.DateField(blank=True, null=True)
    to_date =  models.TimeField(blank=True, null=True)
    count = models.IntegerField(default=1)


class DiscountHandcraft(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    handcraft = models.ForeignKey(Handcraft, on_delete=models.CASCADE)