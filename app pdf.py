import streamlit as st
from fpdf import FPDF
import os

# Configuración de página para móvil
st.set_page_config(page_title="Proforma Alaska", layout="centered")

class PDF(FPDF):
    def header(self):
        # Intentamos cargar logo.png o logo.jpeg
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 30)
        
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'FACTURA PROFORMA', 0, 0, 'C')
        self.ln(20)

def generar_pdf(datos_cliente, items):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Emisor
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Bar Restaurante Alaska / La Chinita", 0, 1)
        pdf.ln(5)

        # Cliente
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Cliente: {datos_cliente['nombre']}", 0, 1)
        pdf.cell(0, 10, f"ID: {datos_cliente['id']}", 0, 1)
        pdf.ln(5)

        # Tabla
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, "Descripcion", 1, 0, 'C', True)
        pdf.cell(30, 10, "Cant.", 1, 0, 'C', True)
        pdf.cell(60, 10, "Total", 1, 1, 'C', True)

        pdf.set_font("Arial", size=10)
        total_general = 0
        for item in items:
            t_linea = item['cantidad'] * item['precio']
            pdf.cell(90, 10, item['nombre'], 1)
            pdf.cell(30, 10, str(item['cantidad']), 1, 0, 'C')
            pdf.cell(60, 10, f"{t_linea:,.2f}", 1, 1, 'R')
            total_general += t_linea

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(120, 10, "TOTAL", 0, 0, 'R')
        pdf.cell(60, 10, f"{total_general:,.2f}", 1, 1, 'R')

        # El truco está aquí: convertir a bytes correctamente
        return pdf.output() 
    except Exception as e:
        return str(e)

# --- Interfaz ---
st.title("📄 Proformas Alaska")

nombre = st.text_input("Nombre del Cliente", key="nom")
cedula = st.text_input("Cédula", key="ced")

st.write("---")
with st.container():
    it_n = st.text_input("Producto")
    col1, col2 = st.columns(2)
    with col1: it_c = st.number_input("Cantidad", min_value=1, value=1)
    with col2: it_p = st.number_input("Precio", min_value=0.0, step=100.0)

if st.button("➕ Agregar", use_container_width=True):
    if 'lista' not in st.session_state: st.session_state.lista = []
    st.session_state.lista.append({"nombre": it_n, "cantidad": it_c, "precio": it_p})
    st.success("Agregado")

if 'lista' in st.session_state and st.session_state.lista:
    st.table(st.session_state.lista)
    
    # Generamos los bytes del PDF antes del botón
    datos = {"nombre": nombre, "id": cedula}
    pdf_data = generar_pdf(datos, st.session_state.lista)
    
    if isinstance(pdf_data, str):
        st.error(f"Error al crear PDF: {pdf_data}")
    else:
        st.download_button(
            label="⬇️ DESCARGAR PROFORMA",
            data=bytes(pdf_data), # Forzamos formato bytes
            file_name=f"Proforma_{nombre}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.button("Limpiar Todo"):
        st.session_state.lista = []
        st.rerun()
