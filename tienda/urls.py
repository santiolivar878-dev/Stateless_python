from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('prenda/<int:prenda_id>/', views.detalle_prenda_view, name='detalle_prenda'),
    path('api/verificar-talla/', views.verificar_talla_api, name='verificar_talla_api'),
    path('probador-3d/', views.probador_3d_view, name='probador_3d'),
    path('api/stylist/', views.stylist_chat_api, name='stylist_chat_api'),
]