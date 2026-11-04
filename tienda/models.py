from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Prenda(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='prendas')
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, default="")
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    
    imagen = models.ImageField(upload_to='prendas/', blank=True, null=True)
    
    color_nombre = models.CharField(max_length=50, default="Negro")
    color_hex = models.CharField(max_length=7, default="#000000")

    archivo_3d = models.CharField(
        max_length=100, 
        blank=True, 
        default="camisa.glb", 
        help_text="Ejemplo: camisa.glb o pantalon.glb"
    )

    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class GuiaTalla(models.Model):
    TALLAS = [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]

    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='guias_talla')
    talla = models.CharField(max_length=5, choices=TALLAS)
    
    altura_min = models.PositiveIntegerField(help_text="Altura mínima recomendada en cm")
    altura_max = models.PositiveIntegerField(help_text="Altura máxima recomendada en cm")

    class Meta:
        unique_together = ('prenda', 'talla')

    def __str__(self):
        return f"{self.prenda.nombre} - Talla {self.talla} ({self.altura_min}-{self.altura_max} cm)"

