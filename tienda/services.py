import json
import os
import time
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.utils.text import slugify
from google import genai
from google.genai import types
from .models import Prenda


def _leer_miniatura(prenda):
    """Convierte la imagen del producto a JPEG ligero (256px) para matching visual."""
    imagen = getattr(prenda, 'imagen', None)
    if not imagen or not getattr(imagen, 'name', ''):
        return None
    try:
        ruta = imagen.path
        if os.path.exists(ruta):
            with Image.open(ruta) as img:
                img = img.convert('RGB')
                img.thumbnail((256, 256))
                buf = BytesIO()
                img.save(buf, format='JPEG', quality=65)
                return buf.getvalue()
    except Exception:
        pass
    return None


def consultar_estilista(mensaje_usuario, imagen_bytes=None, mime_type=None, perfil_estilo=None):
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        return {
            'analisis': 'Falta configurar GEMINI_API_KEY en tu archivo .env.',
            'opciones': []
        }

    prendas = Prenda.objects.select_related('categoria').all()
    catalogo = []
    catalogo_por_slug = {}
    partes_catalogo_visual = []

    for p in prendas:
        slug = slugify(p.nombre) or f"prenda-{p.id}"
        imagen_url = p.imagen.url if getattr(p, 'imagen', None) and p.imagen.name else ''
        item = {
            'nombre': p.nombre,
            'slug': slug,
            'tipo': getattr(p, 'tipo', 'superior'),
            'categoria': p.categoria.nombre if p.categoria else 'General',
            'color': getattr(p, 'color', ''),
            'precio': str(p.precio),
            'descripcion': getattr(p, 'descripcion', ''),
        }
        catalogo.append(item)
        catalogo_por_slug[slug] = {'imagen': imagen_url, 'precio': str(p.precio)}

        # Solo adjuntar miniaturas del catálogo cuando el usuario envía una foto (máx. 4 prendas)
        if imagen_bytes and len(partes_catalogo_visual) < 8:
            thumb = _leer_miniatura(p)
            if thumb:
                partes_catalogo_visual.append(f"Foto de catálogo -> slug='{slug}', nombre='{p.nombre}':")
                partes_catalogo_visual.append(
                    types.Part.from_bytes(data=thumb, mime_type='image/jpeg')
                )

    perfil_texto = "Sin perfil guardado aún."
    if isinstance(perfil_estilo, dict) and perfil_estilo:
        perfil_texto = (
            f"Vibra/Estilo: {perfil_estilo.get('vibra', 'libre')}, "
            f"Fit preferido: {perfil_estilo.get('fit', 'regular')}, "
            f"Paleta favorita: {perfil_estilo.get('paleta', 'neutra')}, "
            f"Ocasión principal: {perfil_estilo.get('ocasion', 'diario')}."
        )

    instruccion_sistema = (
        "Eres el Estilista IA oficial de STATELESS (marca de streetwear de lujo oscuro). "
        "Responde siempre en español con tono cercano, experto en moda urbana y directo. "
        "Analiza la petición del cliente, su perfil de estilo y cualquier foto que envíe (su ropa, tenis o referencia). "
        "Cruza eso con el catálogo real (texto y fotos adjuntas) y recomienda máximo 3 prendas reales "
        "usando EXACTAMENTE sus valores 'slug' y 'tipo' del catálogo.\n\n"
        "Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta:\n"
        "{\n"
        '  "analisis": "Explicación breve y personalizada de por qué estas opciones van con su estilo o foto.",\n'
        '  "opciones": [\n'
        "    {\n"
        '      "titulo": "Nombre exacto de la prenda",\n'
        '      "descripcion": "Cómo combinarla y por qué encaja visualmente con su foto/perfil.",\n'
        '      "slug": "slug-exacto-del-catalogo",\n'
        '      "tipo": "superior o inferior"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    prompt = (
        f"PERFIL DEL CLIENTE (Quiz de estilo): {perfil_texto}\n"
        f"CATÁLOGO DISPONIBLE (JSON): {json.dumps(catalogo, ensure_ascii=False)}\n"
        f"MENSAJE DEL CLIENTE: {mensaje_usuario}"
    )

    contenidos = []
    if imagen_bytes:
        contenidos.append("FOTO ENVIADA POR EL CLIENTE (analiza colores, corte y estilo):")
        contenidos.append(
            types.Part.from_bytes(
                data=imagen_bytes,
                mime_type=mime_type or 'image/jpeg'
            )
        )
    if partes_catalogo_visual:
        contenidos.extend(partes_catalogo_visual)
    contenidos.append(prompt)

    client = genai.Client(api_key=api_key)
    modelos = ['gemini-3.1-flash-lite', 'gemini-flash-latest', 'gemini-4-hydrogen']
    ultimo_error = None

    for modelo in modelos:
        for intento in range(2):
            try:
                config_args = {
                    'system_instruction': instruccion_sistema,
                    'response_mime_type': 'application/json',
                }
                if modelo in ('gemini-flash-latest', 'gemini-4-hydrogen'):
                    config_args['thinking_config'] = types.ThinkingConfig(thinking_level='LOW')

                response = client.models.generate_content(
                    model=modelo,
                    contents=contenidos,
                    config=types.GenerateContentConfig(**config_args)
                )
                texto_json = (response.text or '{}').strip()
                if texto_json.startswith('```'):
                    texto_json = texto_json.strip('`').replace('json\n', '', 1).strip()

                data = json.loads(texto_json)
                for op in data.get('opciones', []):
                    info = catalogo_por_slug.get(op.get('slug', ''), {})
                    op['imagen'] = info.get('imagen', '')
                    op['precio'] = info.get('precio', '')
                return data

            except Exception as e:
                ultimo_error = str(e)
                print(f"[Estilista IA] {modelo} (intento {intento + 1}): {ultimo_error}")
                if ('503' in ultimo_error or 'UNAVAILABLE' in ultimo_error) and intento == 0:
                    time.sleep(0.8)
                    continue
                break

    return {
        'analisis': f'No pude conectar con el estilista en este momento ({ultimo_error}).',
        'opciones': []
    }