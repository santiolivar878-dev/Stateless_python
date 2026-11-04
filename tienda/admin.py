from django.contrib import admin
from .models import Categoria, Prenda, GuiaTalla

# Esto permite editar las tallas dentro de la misma pantalla de la prenda
class GuiaTallaInline(admin.TabularInline):
    model = GuiaTalla
    extra = 4 # Te muestra 4 filas vacías para llenar S, M, L y XL de una vez

@admin.register(Prenda)
class PrendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'color_nombre', 'activo')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [GuiaTallaInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}