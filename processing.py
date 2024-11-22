# processing.py

import os
from dotenv import load_dotenv
import re
import openai
import anthropic
import ell

load_dotenv()

# Configurar las API keys de OpenAI y Anthropic
#openai.api_key = os.getenv('OPENAI_API_KEY')
#anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

# Inicializar ell
ell.init(
    lazy_versioning=True,
    verbose=True
)

# Listas de modelos disponibles
available_models = [
    "gpt-4o",
    "gpt-4o-mini",
    "o1-preview",
    "o1-mini",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022"
]

openai_models = [
    "gpt-4o",
    "gpt-4o-mini",
    "o1-preview",
    "o1-mini"
]

anthropic_models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022"
]

# Registrar modelos de OpenAI (no especificar default_client)
#for model in openai_models:
#    ell.config.register_model(
#        name=model,
#        supports_streaming=False  # Ajusta según sea necesario
#    )

# Crear una instancia del cliente de Anthropic
client_anthropic = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Registrar modelos de Anthropic
for model in anthropic_models:
    ell.config.register_model(
        name=model,
        default_client=client_anthropic,
        supports_streaming=False
    )

def verificar_modelos_registrados():
    for modelo in available_models:
        client, fallback = ell.config.get_client_for(modelo)
        if client:
            print(f"Modelo '{modelo}' registrado correctamente con el cliente '{type(client).__name__}'.")
        else:
            print(f"Modelo '{modelo}' NO está registrado correctamente.")

# Llamar a la función de verificación
verificar_modelos_registrados()

def dividir_texto(texto: str, max_chars: int = 5000) -> list:
    """
    Divide el texto en segmentos de hasta `max_chars` caracteres,
    realizando cortes inteligentes basados en patrones de puntuación y saltos de línea.
    """
    segmentos = []
    longitud_texto = len(texto)
    inicio = 0

    # Definir las prioridades y sus patrones
    prioridades = [
        [r'\.\n'],                # Primera prioridad
        [r'\. ', r'\n', r'; '],   # Segunda prioridad
        [r'\? ', r'! '],          # Tercera prioridad
    ]

    while inicio < longitud_texto:
        fin = min(inicio + max_chars, longitud_texto)
        segmento = texto[inicio:fin]

        if fin < longitud_texto:
            corte_encontrado = False
            corte = fin  # Por defecto, corte en el límite máximo

            # Iterar sobre las prioridades
            for patrones in prioridades:
                # Buscar todas las ocurrencias de los patrones en la prioridad actual
                indices_cortes = []
                for patron in patrones:
                    matches = list(re.finditer(patron, segmento))
                    if matches:
                        # Tomar el último match para maximizar el tamaño del segmento
                        ultimo_match = matches[-1]
                        indices_cortes.append(ultimo_match.end())

                if indices_cortes:
                    # Tomar el corte más grande encontrado en esta prioridad
                    corte_relativo = max(indices_cortes)
                    corte = inicio + corte_relativo
                    corte_encontrado = True
                    break  # Salir del bucle de prioridades si encontramos un corte

            # Si no se encontró ningún patrón en todas las prioridades, `corte` ya está establecido en `fin`
        else:
            # Último segmento, cortar hasta el final del texto
            corte = longitud_texto

        # Añadir el segmento a la lista
        segmentos.append(texto[inicio:corte].strip())
        inicio = corte

    return segmentos

def traducir_segmento(modelo: str, segmento_actual: str, contexto_anterior: str, contexto_posterior: str, idioma: str) -> str:
    """
    Concisa un segmento de texto utilizando el modelo y el idioma especificados.
    """
    # Definir el valor de max_tokens para modelos de Anthropic
    max_tokens = 8000 if modelo in anthropic_models else None

    # Construir los argumentos para el decorador
    decorator_kwargs = {'model': modelo}
    if max_tokens is not None:
        decorator_kwargs['max_tokens'] = max_tokens

    # Aplicar el decorador con los argumentos apropiados
    decorator = ell.simple(**decorator_kwargs)

    @decorator
    def _traducir(segmento_actual, contexto_anterior, contexto_posterior):
        # Construir el prompt según el idioma
        if idioma == "Español Conciso":
            prompt = f"""
Traduce el siguiente texto al español conciso, preservando la integridad informativa con la menor cantidad posible de caracteres.
No omitas detalles clave, especialmente en listas. Reduce palabras sin resumir. Utiliza abreviaturas cuando sea posible, sin perder claridad.
No uses formatos de énfasis como negritas. Omite metadatos, enlaces y referencias.
Tanto el contexto previo como el posterior son para que el inicio y el final del segmento actual tengan una transición de estilo y coherencia; sin embargo, la salida debe ser solo la traducción del segmento actual, no de los contextos.
En la salida imprime solo el texto traducido, sin ningún tipo de encabezado, ni metatexto.

Contexto Previo:
<contexto_anterior>
{contexto_anterior}
</contexto_anterior>

Contexto Posterior:
<contexto_posterior>
{contexto_posterior}
</contexto_posterior>

Segmento a Traducir:
<segmento_actual>
{segmento_actual}
</segmento_actual>
"""
        elif idioma == "Inglés Conciso":
            prompt = f"""
Translate the following text into concise English, preserving informational integrity with the minimum possible characters.
Do not omit key details, especially in lists. Reduce words without summarizing. Use abbreviations when possible, without losing clarity.
Do not use bold or other emphasis formats. Omit metadata, links, and references.
Both the previous and subsequent context are so that the beginning and end of the current segment have a transition of style and thematic coherence; however, the output must be only the translation of the current segment, not of the contexts.
In the output prints only the translated text, without any type of header or metatext.

Previous Context:
<contexto_anterior>
{contexto_anterior}
</contexto_anterior>

Subsequent Context:
<contexto_posterior>
{contexto_posterior}
</contexto_posterior>

Segment to Translate:
<segmento_actual>
{segmento_actual}
</segmento_actual>
"""
        else:
            raise ValueError("Idioma no soportado.")

        return prompt

    # Llamar a la función interna y devolver la traducción
    traduccion = _traducir(segmento_actual, contexto_anterior, contexto_posterior)
    return traduccion.strip()
