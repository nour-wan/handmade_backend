from django.db import models

# Create your models here.

class Category(models.Model):
    
    category_name=models.CharField(max_length = 200 )
    category_description=models.TextField(max_length = 1000 ,default="",blank=False)
    categorye_image=models.ImageField(upload_to= 'categories_images/')
    
    
    
    def __str__(self):
        return self.name    