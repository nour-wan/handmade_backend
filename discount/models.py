from django.db import models

from maker.models import Maker

# Create your models here.
class Discount(models.Model):
    maker = models.ForeignKey(Maker, on_delete = models.CASCADE,blank=True, null=True)
    name = models.CharField(max_length = 50)
    precentage = models.FloatField()
    from_date = models.CharField(max_length = 50)
    to_date = models.CharField(max_length = 50)
    count = models.IntegerField(default=1)


