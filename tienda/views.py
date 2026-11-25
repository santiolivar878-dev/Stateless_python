import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.text import slugify
from .models import Prenda, GuiaTalla
from .services import consultar_estilista


def inicio_view(request):
    prendas = Prenda.objects.all()
    return render(request, 'tienda/inicio.html', {'prendas': prendas})


def detalle_prenda_view(request, prenda_id):
    prenda = get_object_or_404(Prenda, id=prenda_id)
    return render(request, 'tienda/detalle.html', {'prenda': prenda})


def verificar_talla_api(request):
    prenda_id = request.GET.get('prenda_id')
    try:
        altura = int(request.GET.get('altura', 175))
    except ValueError:
        return JsonResponse({'error': 'Altura inválida'}, status=400)

    guias = GuiaTalla.objects.filter(prenda_id=prenda_id)
    talla_rec = 'M'
    if guias.exists():
        for g in guias:
            if g.estatura_min <= altura <= g.estatura_max:
                talla_rec = g.talla
                break
    else:
        if altura < 168:
            talla_rec = 'S'
        elif altura <= 178:
            talla_rec = 'M'
        elif altura <= 186:
            talla_rec = 'L'
        else:
            talla_rec = 'XL'

    return JsonResponse({'talla_recomendada': talla_rec})


def probador_3d_view(request):
    prendas = Prenda.objects.all()
    catalogo_3d = {}

    for p in prendas:
        slug = slugify(p.nombre) or f"prenda-{p.id}"
        archivo = (p.modelo_3d or 'camisa-polo-fuenza_blanca.glb').strip()
        if '/' in archivo:
            archivo = archivo.split('/')[-1]
        if not archivo.lower().endswith(('.glb', '.gltf')):
            archivo += '.glb'

        catalogo_3d[slug] = {
            'id': p.id,
            'nombre': p.nombre,
            'slug': slug,
            'tipo': p.tipo,
            'precio': str(p.precio),
            'color': p.color,
            'modelo': f"/static/modelos/{archivo}",
            'modelo_nombre': archivo,
        }

    return render(request, 'tienda/probador.html', {
        'catalogo_3d': catalogo_3d,
        'prendas': prendas,
    })


def stylist_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    mensaje = ''
    imagen_bytes = None
    mime_type = None

    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body)
            mensaje = data.get('mensaje', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
    else:
        mensaje = request.POST.get('mensaje', '').strip()
        imagen = request.FILES.get('imagen')
        if imagen:
            imagen_bytes = imagen.read()
            mime_type = imagen.content_type

    if not mensaje and not imagen_bytes:
        return JsonResponse({'error': 'Escribe un mensaje o sube una foto.'}, status=400)

    respuesta = consultar_estilista(
        mensaje_usuario=mensaje or 'Recomiéndame cómo combinar esta prenda del catálogo.',
        imagen_bytes=imagen_bytes,
        mime_type=mime_type,
    )
    return JsonResponse(respuesta)