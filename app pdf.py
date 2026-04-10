import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
import pytz

st.set_page_config(page_title="Proforma Grúas Mau", layout="centered")
local_tz = pytz.timezone('America/Costa_Rica')

class PDF(FPDF):
    def header(self):
        # --- LOGO CENTRADO Y MUCHO MÁS GRANDE (Tamaño 80) ---
        if os.path.exists("logo.png"):
            # Calculamos la posición X para centrarlo
            # Ancho página (210) - Ancho logo (80) / 2 = 65
            self.image("logo.png", 65, 8, 80) 
            self.ln(35) # Espacio grande hacia abajo para no tapar nada
        else:
            self.ln(10) # Si no hay logo, espacio normal

        # Título y Fecha alineados a la derecha
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FACTURA PROFORMA', 0, 1, 'R')
        self.set_font('Arial', '', 10)
        ahora_cr = datetime.now(local_tz)
        num_proforma = ahora_cr.strftime("%Y%m%d-%H%M")
        fecha_hoy = ahora_cr.strftime("%d/%m/%Y %I:%M %p")
        self.cell(0, 5, f'Proforma N°: {num_proforma}', 0, 1, 'R')
        self.cell(0, 5, f'Fecha: {fecha_hoy}', 0, 1, 'R')
        self.ln(15) 

def generar_pdf(datos_cliente, items, info_adicional, aplicar_iva):
    try:
        pdf = PDF()
        pdf.add_page()
        # El encabezado ya se generó solo

        # --- DATOS DEL EMISOR ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, "GRÚAS MAU - SERVICIO 24/7", 0, 1)
        pdf.set_font("Arial", size=9)
        # Tilses agregadas para profesionalismo
        pdf.cell(0, 5, "Teléfonos: 8875-5921 / 6231-2471 / 8438-2706", 0, 1)
        pdf.cell(0, 5, "Emails: Mau27@gmail.com / Jossimedra@gmail.com", 0, 1)
        pdf.ln(10)

        # --- DATOS DEL CLIENTE ---
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 7, " DATOS DEL CLIENTE", 0, 1, 'L', True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 7, f"Empresa/Nombre: {datos_cliente['nombre']}", 0, 1)
        pdf.cell(0, 7, f"NIT / Cédula: {datos_cliente['id']}", 0, 1)
        pdf.cell(0, 7, f"Teléfono / Fax: {info_adicional['tel']}", 0, 1)
        pdf.ln(5)

        # --- DETALLE DEL SERVICIO ---
        pdf.set_fill_color(30, 30, 30)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        # Forzamos los acentos en la tabla usando codificación manual
        pdf.cell(90, 10, u" DESCRIPCIÓN DEL SERVICIO".encode('latin1').decode('utf-8'), 1, 0, 'L', True)
        pdf.cell(25, 10, "CANT.", 1, 0, 'C', True)
        pdf.cell(35, 10, "PRECIO UNIT.", 1, 0, 'C', True)
        pdf.cell(40, 10, "TOTAL", 1, 1, 'C', True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        subtotal = 0
        for item in items:
            t_linea = item['cantidad'] * item['precio']
            # Para la descripción, intentamos codificar para acentos
            try:
                desc_segura = item['nombre'].encode('latin1', 'replace').decode('latin1')
            except:
                desc_segura = item['nombre']
                
            pdf.cell(90, 10, desc_segura, 1)
            pdf.cell(25, 10, str(item['cantidad']), 1, 0, 'C')
            pdf.cell(35, 10, f"{item['precio']:,.2f}", 1, 0, 'R')
            pdf.cell(40, 10, f"{t_linea:,.2f}", 1, 1, 'R')
            subtotal += t_linea

        # --- TOTALES ---
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        if aplicar_iva:
            impuestos = subtotal * 0.13
            total_pagar = subtotal + impuestos
            pdf.cell(150, 8, "SUBTOTAL: ", 0, 0, 'R')
            pdf.cell(40, 8, f"{subtotal:,.2f}", 1, 1, 'R')
            pdf.cell(150, 8, "IMPUESTOS (13%): ", 0, 0, 'R')
            pdf.cell(40, 8, f"{impuestos:,.2f}", 1, 1, 'R')
        else:
            total_pagar = subtotal
        
        # Color dorado para el total
        pdf.set_fill_color(255, 215, 0)
        pdf.cell(150, 10, "TOTAL A PAGAR: ", 0, 0, 'R')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, f"{total_pagar:,.2f}", 1, 1, 'R', True)

        return pdf.output()
    except Exception as e:
        return str(e)

# --- INTERFAZ STREAMLIT ---
st.title("🚜 Grúas Mau - Proformas")
with st.expander("Datos del Cliente", expanded=True):
    nom = st.text_input("Empresa / Nombre")
    ced = st.text_input("NIT / Cédula")
    tel = st.text_input("Teléfono / Fax")

st.divider()
aplicar_iva = st.checkbox("¿Aplicar el 13% de IVA?", value=True)

st.subheader("Detalle del Servicio")
it_n = st.text_input("Descripción del servicio")
col1, col2 = st.columns(2)
with col1: it_c = st.number_input("Cantidad", min_value=1, value=1)
with col2: it_p = st.number_input("Precio Unitario", min_value=0.0, step=1000.0)

if st.button("➕ Agregar a la Tabla", use_container_width=True):
    if 'lista' not in st.session_state: st.session_state.lista = []
    # Guardamos el texto sin procesar para mostrarlo en st.table
    st.session_state.lista.append({"nombre": it_n, "cantidad": it_c, "precio": it_p})
    st.toast("Añadido")

if 'lista' in st.session_state and st.session_state.lista:
    st.table(st.session_state.lista)
    
    # Datos para PDF
    pdf_data = generar_pdf({"nombre": nom, "id": ced}, st.session_state.lista, {"tel": tel}, aplicar_iva)
    
    if isinstance(pdf_data, str):
        st.error(f"Error: {pdf_data}")
    else:
        # Nombre del archivo con hora CR
        ahora_cr_file = datetime.now(local_tz).strftime('%H%M')
        # Limpiamos el nombre de espacios
        nom_seguro = nom.replace(" ", "_") if nom else "Cliente"
        archivo_nombre = f"Proforma_{nom_seguro}_{ahora_cr_file}.pdf"
        
        st.download_button(
            label="💾 GENERAR Y DESCARGAR PDF",
            data=bytes(pdf_data),
            file_name=archivo_nombre,
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    if st.button("Limpiar y Nueva Proforma", use_container_width=True):
        st.session_state.lista = []
        st.rerun()
