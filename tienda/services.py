from google import genai
from google.genai import types
from django.conf import settings
from django.utils.text import slugify
from .models import Prenda
import json
import time

def obtener_catalogo_contexto():
    prendas = Prenda.objects.all()
    lista = []
    for p in prendas:
        lista.append({
            "nombre": p.nombre,
            "slug": slugify(p.nombre),
            "tipo": p.tipo,
            "categoria": p.categoria.nombre if p.categoria else "Streetwear",
            "precio": float(p.precio),
            "color": p.color,
            "descripcion": p.descripcion,
        })
    return json.dumps(lista, ensure_ascii=False)

def consultar_estilista(mensaje_usuario, imagen_bytes=None, mime_type=None):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    catalogo = obtener_catalogo_contexto()

    system_instruction = f"""
    Eres el Director Creativo y Estilista Senior de "STATELESS", marca de luxury dark streetwear.
    
    Catálogo oficial actual en stock (USA SIEMPRE EL "slug" EXACTO DE ESTE LISTADO):
    {catalogo}
    
    Tus tareas:
    1. Si el usuario sube una foto: analiza la prenda (colorimetría, textura y silueta).
    2. Explica con criterio de moda cómo combinarla usando prendas del catálogo (máximo 2 párrafos cortos en español).
    3. Entrega hasta 3 opciones reales del catálogo para probar en el modelo 3D.
    
    FORMATO OBLIGATORIO (JSON puro sin markdown):
    {{
      "analisis": "Tu análisis y consejo de moda aquí.",
      "opciones": [
        {{
          "titulo": "Nombre exacto de la prenda",
          "descripcion": "Por qué combina bien con el look.",
          "slug": "slug-exacto-del-catalogo",
          "tipo": "superior"
        }}
      ]
    }}
    Nota: En "tipo" pon "superior" o "inferior" según corresponda en el catálogo.
    """

    contents = []
    if imagen_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=imagen_bytes, mime_type=mime_type))
    contents.append(mensaje_usuario)

    modelos_disponibles = ['gemini-3.8-flash', 'gemini-flash-latest', 'gemini-3.1-flash-lite']

    for modelo in modelos_disponibles:
        try:
            config_kwargs = {
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
            }
            if modelo == 'gemini-3.8-flash':
                config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level="LOW")

            response = client.models.generate_content(
                model=modelo,
                contents=contents,
                config=types.GenerateContentConfig(**config_kwargs)
            )

            raw_text = (response.text or "").strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            return json.loads(raw_text.strip())
        except Exception:
            time.sleep(1)
            continue

    return {
        "analisis": "Te sugiero contrastar volúmenes combinando nuestras prendas superiores e inferiores.",
        "opciones": []
    }