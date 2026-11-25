from google import genai
from google.genai import types
from django.conf import settings
from .models import Prenda
import json
import time

def obtener_catalogo_contexto():
    prendas = Prenda.objects.all()
    lista = []
    for p in prendas:
        lista.append({
            "nombre": getattr(p, 'nombre', 'Prenda'),
            "categoria": p.categoria.nombre if getattr(p, 'categoria', None) else "Streetwear",
            "precio": float(getattr(p, 'precio', 0)),
            "color": getattr(p, 'color', 'Negro'),
            "descripcion": getattr(p, 'descripcion', 'Prenda STATELESS'),
            "slug": p.nombre.lower().replace(" ", "-") if hasattr(p, 'nombre') else "prenda"
        })
    return json.dumps(lista, ensure_ascii=False)

def consultar_estilista(mensaje_usuario, imagen_bytes=None, mime_type=None):
    """
    Analiza imagen y texto devolviendo 3 opciones interactivas con fallback anti-503.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    catalogo = obtener_catalogo_contexto()

    system_instruction = f"""
    Eres el Director Creativo y Estilista Senior de "STATELESS", marca de luxury dark streetwear.
    
    Catálogo oficial en stock:
    {catalogo}
    
    Tus tareas obligatorias:
    1. Si el usuario sube una foto: analiza la prenda (colorimetría, tela, textura y silueta).
    2. Explica con criterio de diseñador de modas cómo elevar ese look usando STATELESS.
    3. Entrega SIEMPRE 3 opciones concretas de combinación que el usuario pueda probar en el modelo 3D.
    
    FORMATO DE RESPUESTA OBLIGATORIO (JSON puro sin markdown):
    Debes responder ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
    {{
      "analisis": "Tu análisis de la prenda y recomendación de moda (máximo 2 párrafos).",
      "opciones": [
        {{
          "titulo": "Camisa Polo Octane",
          "descripcion": "Contraste limpio y estructura regular.",
          "accion": "probar_camisa"
        }},
        {{
          "titulo": "Pantalón Octane Wide Leg",
          "descripcion": "Caída ancha techwear para balancear la silueta.",
          "accion": "probar_pantalon"
        }},
        {{
          "titulo": "Outfit Completo Octane",
          "descripcion": "El conjunto insignia completo de STATELESS.",
          "accion": "probar_outfit"
        }}
      ]
    }}
    """

    contents = []
    if imagen_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=imagen_bytes, mime_type=mime_type))
    contents.append(mensaje_usuario)

    # Lista de modelos con fallback en caso de 503 o saturación
    modelos_disponibles = ['gemini-flash-latest', 'gemini-3.8-flash', 'gemini-3.1-flash-lite']
    ultimo_error = None

    for modelo in modelos_disponibles:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json", # Exige JSON estructurado
                )
            )

            raw_text = response.text.strip()
            # Limpiar posibles bloques markdown si los agrega
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            datos = json.loads(raw_text.strip())
            return datos

        except Exception as e:
            ultimo_error = e
            time.sleep(1) # Pequeña pausa antes de probar el siguiente modelo
            continue

    # Si todos fallaron por caída de servidores, respuesta de contingencia elegante
    return {
        "analisis": "Veo una prenda versátil. Para un estilo streetwear de impacto, te sugiero contrastarla con los cortes oscuros y minimalistas de STATELESS.",
        "opciones": [
            {"titulo": "Camisa Polo Octane", "descripcion": "Corte regular fit minimalista.", "accion": "probar_camisa"},
            {"titulo": "Pantalón Octane", "descripcion": "Corte wide leg holgado.", "accion": "probar_pantalon"},
            {"titulo": "Outfit Completo", "descripcion": "Ver ambas prendas combinadas.", "accion": "probar_outfit"}
        ]
    }