from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'chest_width', 'shoulder_width', 'garment_length', 'created_at')
    search_fields = ('name', 'description')
    
    # Esto agrupa los campos ordenadamente dentro del formulario de edición en el Admin
    fieldsets = (
        ('Información Principal', {
            'fields': ('name', 'price', 'description', 'image', 'model_3d')
        }),
        ('Dimensiones y Tallas (Fit Finder)', {
            'fields': ('chest_width', 'shoulder_width', 'garment_length'),
            'description': 'Medidas técnicas de la prenda en centímetros (cm) para el sistema de ajuste virtual.'
        }),
    )