from django.contrib import admin
from .models import Categoria, Prenda, GuiaTalla

class GuiaTallaInline(admin.TabularInline):
    model = GuiaTalla
    extra = 1

@admin.register(Prenda)
class PrendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'tipo', 'modelo_3d', 'precio', 'color')
    inlines = [GuiaTallaInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)