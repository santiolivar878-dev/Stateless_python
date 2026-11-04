from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Conecta la raíz de la web a tu app de tienda:
    path('', include('tienda.urls')),
]