import streamlit as st
from fpdf import FPDF
import os

# Configuración de la página para móvil
st.set_page_config(page_title="Proforma Móvil", layout="centered")

class PDF(FPDF):
    def header(self):
        # Intentar cargar el logo si existe
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'FACTURA PROFORMA', 0, 0, 'C')
        self.ln(20)

def generar_pdf(datos_cliente, items):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Datos del Emisor
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Emisor: Tu Negocio", 0, 1)
    pdf.ln(5)

    # Datos del Cliente
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, f"Cliente: {datos_cliente['nombre']}", 0, 1)
    pdf.cell(0, 10, f"ID/Cédula: {datos_cliente['id']}", 0, 1)
    pdf.ln(5)

    # Tabla optimizada
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Descripción", 1, 0, 'C', True)
    pdf.cell(30, 10, "Cant.", 1, 0, 'C', True)
    pdf.cell(60, 10, "Total", 1, 1, 'C', True)

    pdf.set_font("Arial", size=10)
    total_general = 0
    for item in items:
        total_linea = item['cantidad'] * item['precio']
        pdf.cell(90, 10, item['nombre'], 1)
        pdf.cell(30, 10, str(item['cantidad']), 1, 0, 'C')
        pdf.cell(60, 10, f"{total_linea:,.2f}", 1, 1, 'R')
        total_general += total_linea

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(120, 10, "TOTAL FINAL", 0, 0, 'R')
    pdf.cell(60, 10, f"{total_general:,.2f}", 1, 1, 'R')

    return pdf.output(dest='S')

# --- INTERFAZ PARA MÓVIL ---
st.title("📄 Generador Proforma")

# Formulario simple
nombre = st.text_input("Nombre del Cliente")
cedula = st.text_input("Identificación")

st.divider()

# Entrada de productos
with st.container():
    item_n = st.text_input("Producto/Servicio")
    c1, c2 = st.columns(2)
    with c1: item_c = st.number_input("Cantidad", min_value=1, value=1)
    with c2: item_p = st.number_input("Precio unit.", min_value=0.0)

if st.button("➕ Agregar Producto", use_container_width=True):
    if 'items_movil' not in st.session_state:
        st.session_state.items_movil = []
    st.session_state.items_movil.append({"nombre": item_n, "cantidad": item_c, "precio": item_p})
    st.success("Agregado")

# Mostrar lista y generar
if 'items_movil' in st.session_state and st.session_state.items_movil:
    st.write("---")
    for i, x in enumerate(st.session_state.items_movil):
        st.write(f"{x['cantidad']}x {x['nombre']} - {x['precio']*x['cantidad']:,.2f}")
    
    if st.button("💾 GENERAR Y DESCARGAR PDF", type="primary", use_container_width=True):
        datos = {"nombre": nombre, "id": cedula}
        pdf_bytes = generar_pdf(datos, st.session_state.items_movil)
        
        st.download_button(
            label="⬇️ Click aquí para guardar en celular",
            data=pdf_bytes,
            file_name=f"Proforma_{nombre}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    if st.button("Limpiar lista", use_container_width=True):
        st.session_state.items_movil = []
        st.rerun()