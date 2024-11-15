import ell
import os
from dotenv import load_dotenv
import re

load_dotenv()

ell.init(
    default_api_params={'temperature': 0.0},
    lazy_versioning=True,
    verbose=True
)

try:

    def dividir_texto(texto, max_chars=7000):
        """
        Divide el texto en segmentos de hasta `max_chars` caracteres,
        realizando cortes inteligentes basados en patrones de puntuación y saltos de línea.

        Prioridades de corte:
        1. Primera prioridad:
           - ".\n"
        2. Segunda prioridad:
           - ". ", "\n", "; "
        3. Tercera prioridad:
           - "? ", "! "
        4. Última prioridad:
           - Corte forzado en el límite máximo si no se encuentran las marcas anteriores.
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



except Exception as e:
    st.error(f"Ocurrió un error: {e}")  



@ell.simple(model="gpt-4o", max_tokens = 8000)
def traducir_segmento(segmento_actual, contexto_anterior, contexto_posterior):
    """Eres un traductor experto que produce traducciones al español conciso."""
    prompt = f"""
        Translate the following text into Spanish, preserving the informational integrity with the minimum possible characters.
        Do not omit key details, especially in lists. Reduce words without summarizing. Use abbreviations when possible, without losing clarity.
        Do not use bold or other emphasis formats. Omit metadata, links, and references.
        Both the previous and subsequent context are so that the beginning and end of the current segment has a transition of style and coherence, however the output must be only of translated current segment. Not of the contexts.

    A continuación el contexto previo del segmento que debes traducir. Debes tenerlo en mente para que la traducción del segmento actual siga en estilo y coherencia temática este contexto previo:
    
    <contexto_anterior>
    {contexto_anterior}
    </contexto_anterior>

    A continuación el contexto posterior del segmento que debes traducir. Debes tenerlo en mente para que la traducción del segmento actual en su parte final se ajuste en continuidad al texto que le sigue:
    
    <contexto_posterior>
    {contexto_posterior}
    </contexto_posterior>
    
    A continuación el segemnto que que debes traducir a español, considerando el contexto anterior y posterior:
    
    <segmento_actual>
    {segmento_actual}
    </segmento_actual>
    """
    return prompt
