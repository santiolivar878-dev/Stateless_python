import os
from google import genai
from django.db import models  # 👈 Corregido a models (en plural)

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    model_3d = models.FileField(upload_to='products/models_3d/', blank=True, null=True)
    chest_width = models.FloatField(help_text="Ancho de pecho en cm", default=50.0)
    shoulder_width = models.FloatField(help_text="Ancho de hombros en cm", default=45.0)
    garment_length = models.FloatField(help_text="Largo de la prenda en cm", default=70.0)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Si no hay descripción y tenemos el nombre, generamos con Gemini UNA SOLA VEZ al guardar
        if not self.description and self.name:
            try:
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                response = client.models.generate_content(
                    model='gemini-1.5-flash',  # 👈 Usamos 1.5-flash que es el más estable y disponible
                    contents=f"Redacta una descripción comercial corta y atractiva de estilo cyberpunk/techwear para una prenda de ropa llamada: {self.name}."
                )
                self.description = response.text
            except Exception as e:
                print("--- ERROR DE GEMINI EN ADMIN ---", e)
                # Si la IA falla, le ponemos una descripción predeterminada genial para que no quede vacía
                self.description = f"Prenda exclusiva de la colección STATELESS. Diseño {self.name} de alta gama con estética techwear y acabados urbanos."
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name