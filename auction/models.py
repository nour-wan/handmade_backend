from django.db import models

# Create your models here.
from django.db import models

from handcrafts.models import Handcraft
from maker.models import Maker



class Auction(models.Model):
    name = models.CharField(max_length=200)
    location = models.TextField()
    description = models.TextField()
    from_date = models.DateTimeField(auto_now_add=True)
    to_date = models.DateTimeField()
 

class MakerAuction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

class AuctionHandcraft(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE,blank=True, null=True)
    handcraft = models.ForeignKey(Handcraft, on_delete=models.CASCADE)