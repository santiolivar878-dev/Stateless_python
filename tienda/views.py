from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Prenda, Categoria, GuiaTalla

# 1. Vista de Inicio / Catálogo
def inicio_view(request):
    prendas = Prenda.objects.filter(activo=True)
    categorias = Categoria.objects.all()
    return render(request, 'tienda/inicio.html', {
        'prendas': prendas,
        'categorias': categorias,
    })

# 2. Vista de Detalle de Producto
def detalle_prenda_view(request, slug):
    prenda = get_object_or_404(Prenda, slug=slug, activo=True)
    tallas_disponibles = ['S', 'M', 'L', 'XL']
    return render(request, 'tienda/detalle.html', {
        'prenda': prenda,
        'tallas': tallas_disponibles,
    })

# 3. Función Matemática que verifica la talla y responde por JSON
def verificar_talla_api(request):
    prenda_id = request.GET.get('prenda_id')
    talla_elegida = request.GET.get('talla')
    altura_str = request.GET.get('altura')

    if not altura_str or not prenda_id or not talla_elegida:
        return JsonResponse({'mensaje': ''})

    try:
        altura = int(altura_str)
    except ValueError:
        return JsonResponse({'mensaje': 'Ingresa una altura válida en números.'})

    # Buscamos la regla para esa talla
    regla = GuiaTalla.objects.filter(prenda_id=prenda_id, talla=talla_elegida).first()

    if not regla:
        return JsonResponse({'mensaje': f'Talla {talla_elegida} seleccionada.'})

    # Si es más alto que el máximo de la prenda
    if altura > regla.altura_max:
        talla_correcta = GuiaTalla.objects.filter(
            prenda_id=prenda_id,
            altura_min__lte=altura,
            altura_max__gte=altura
        ).first()

        sugerencia = talla_correcta.talla if talla_correcta else "L o XL"
        diferencia = altura - regla.altura_max

        return JsonResponse({
            'alerta': True,
            'mensaje': f'⚠️ Ojo: Para tus {altura} cm, la talla {talla_elegida} te quedará corta de largo (unos {diferencia} cm menos de caída). Te sugerimos probar la talla {sugerencia}.'
        })

    # Si es más bajo que el mínimo
    elif altura < regla.altura_min:
        return JsonResponse({
            'alerta': True,
            'mensaje': f'ℹ️ Para tus {altura} cm, la talla {talla_elegida} te quedará bastante larga y holgada. Considera una talla menor si no buscas un corte muy oversize.'
        })

    # Talla ideal
    else:
        return JsonResponse({
            'alerta': False,
            'mensaje': f'✅ ¡La talla {talla_elegida} es perfecta para tu altura ({altura} cm)!'
        })

    # 4. Vista del Probador Virtual 3D
def probador_3d_view(request):
    slug_prenda = request.GET.get('prenda')
    altura_inicial = request.GET.get('altura', '175') # Altura base por defecto: 175 cm

    prenda = None
    if slug_prenda:
        prenda = Prenda.objects.filter(slug=slug_prenda, activo=True).first()

    return render(request, 'tienda/probador.html', {
        'prenda': prenda,
        'altura_inicial': altura_inicial,
    })