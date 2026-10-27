from django.db import models
from .gemini_service import generate_product_description

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    model_3d = models.FileField(upload_to='products/models_3d/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Si no hay descripción escrita, pedimos a Gemini que la cree basada en el nombre
        if not self.description and self.name:
            self.description = generate_product_description(self.name)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        