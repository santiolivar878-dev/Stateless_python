from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Prenda(models.Model):
    TIPO_CHOICES = [
        ('superior', 'Parte Superior (Camisa / Hoodie / Chaqueta)'),
        ('inferior', 'Parte Inferior (Pantalón / Cargo / Short)'),
    ]

    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='prendas')
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    color = models.CharField(max_length=50, default="Negro")
    descripcion = models.TextField(blank=True, default="Prenda streetwear de diseño minimalista STATELESS.")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='superior')
    modelo_3d = models.CharField(
        max_length=200,
        default="camisa-polo-fuenza_blanca.glb",
        help_text="Nombre exacto del archivo .glb dentro de static/modelos/"
    )

    def __str__(self):
        return self.nombre


class GuiaTalla(models.Model):
    TALLAS = [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='guias_talla')
    talla = models.CharField(max_length=5, choices=TALLAS)
    altura_min_cm = models.IntegerField(default=165)
    altura_max_cm = models.IntegerField(default=180)
    pecho_cm = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.prenda.nombre} - Talla {self.talla}"