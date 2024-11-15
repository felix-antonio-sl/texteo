import streamlit as st
from processing import dividir_texto, traducir_segmento
from dotenv import load_dotenv
from fpdf import FPDF
import io

# Cargar variables de entorno
load_dotenv()

st.set_page_config(page_title="Procesamiento y Traducción de Texto", layout="wide")

st.title("Procesamiento y Traducción de Texto")

# Entrada de texto por parte del usuario
texto_input = st.text_area("Ingrese el texto a procesar:", height=300)

# Opción para cargar un archivo de texto
uploaded_file = st.file_uploader("O cargue un archivo de texto", type=["txt"])
if uploaded_file is not None:
    texto_input = uploaded_file.read().decode('utf-8')

if st.button("Procesar Texto") and texto_input:
    with st.spinner("Procesando..."):
        try:
            # División del texto en segmentos
            segmentos = dividir_texto(texto_input)
            num_segmentos = len(segmentos)
            st.write(f"El texto se ha dividido en {num_segmentos} segmentos.")

            # Variables para almacenar los resultados
            traducciones = []
            contexto_anterior = ""

            # Barra de progreso
            progreso = st.progress(0)

            for i, segmento in enumerate(segmentos):
                contexto_posterior = segmentos[i + 1][:500] if i + 1 < num_segmentos else ""
                traduccion = traducir_segmento(
                    segmento_actual=segmento,
                    contexto_anterior=contexto_anterior[-1000:],
                    contexto_posterior=contexto_posterior
                )
                traducciones.append(traduccion)
                # Actualizar el contexto anterior
                contexto_anterior += traduccion
                # Actualizar barra de progreso
                progreso.progress((i + 1) / num_segmentos)

            # Mostrar el texto traducido completo
            texto_traducido = "\n".join(traducciones)
            st.subheader("Texto Traducido:")
            st.write(texto_traducido)

            # Botón de descarga en TXT
            st.download_button(
                label="Descargar Texto Traducido (TXT)",
                data=texto_traducido,
                file_name='texto_traducido.txt',
                mime='text/plain'
            )

            # Botón de descarga en PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            # Añadir texto al PDF
            for line in texto_traducido.split('\n'):
                pdf.multi_cell(0, 10, line)

            # Guardar el PDF en un buffer
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            pdf_data = pdf_buffer.getvalue()

            st.download_button(
                label="Descargar Texto Traducido (PDF)",
                data=pdf_data,
                file_name='texto_traducido.pdf',
                mime='application/pdf'
            )

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
