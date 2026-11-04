from google import genai
from django.conf import settings

def generate_product_description(product_name):
    """
    Usa Google Gemini Flash para redactar una descripción de marketing 
    atractiva para una prenda o producto de la tienda STATELESS.
    """
    try:
        # Inicializamos el cliente oficial de Google GenAI con tu API Key
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"Actúa como experto en marketing de moda urbana y escribe una descripción corta, moderna y atractiva en español para una prenda de e-commerce llamada '{product_name}'."
        
        # Llamada al modelo Gemini 2.5 / Flash más rápido y eficiente
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )

        return response.text
    except Exception as e:
        return f"No se pudo generar la descripción con IA en este momento. Error: {str(e)}"