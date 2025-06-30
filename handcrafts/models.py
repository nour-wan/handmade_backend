from django.db import models

from categories.models import Category
from maker.models import Maker

# Create your models here.
class Handcraft(models.Model):
    handcraft_name=models.CharField(max_length=255)
    handcraft_price=models.DecimalField(max_digits=10, decimal_places=2)
    handcraft_count=models.IntegerField()
    handcraft_image=models.ImageField(upload_to= 'handcraft_images/')
    category = models.ForeignKey(Category, on_delete = models.CASCADE)  
    maker = models.ForeignKey(Maker, on_delete = models.PROTECT,null= True , blank=True)  
    is_indexed = models.BooleanField(default=False,null= True , blank=True)
    # handcraft_cost=models.DecimalField(max_digits=10, decimal_places=2,null= True , blank=True)

    def __str__(self):
        return self.handcraft_name

    @property
    def image_url(self):
        return self.image.url # للحصول على URL الصورة

    @property
    def image_path(self):
        return self.image.path # للحصول على المسار الفعلي للصورة

# class HandcraftImage(models.Model):
#     Handcraft = models.ForeignKey(Handcraft, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='handcraft_images/')
#     caption = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         return f"Image for {self.product.name}"    