import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
import pytz

# Configuración de página
st.set_page_config(page_title="Proforma Grúas Mau", layout="centered")
local_tz = pytz.timezone('America/Costa_Rica')

# --- FUNCIÓN PARA REINICIAR TODO ---
def reiniciar_aplicacion():
    # Borra todas las variables guardadas en la sesión
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

class PDF(FPDF):
    def header(self):
        # Logo centrado tamaño 100
        if os.path.exists("logo.png"):
            self.image("logo.png", 55, 10, 100) 
            self.ln(50)
        
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FACTURA PROFORMA', 0, 1, 'R')
        self.set_font('Arial', '', 10)
        ahora_cr = datetime.now(local_tz)
        num_proforma = ahora_cr.strftime("%Y%m%d-%H%M")
        fecha_hoy = ahora_cr.strftime("%d/%m/%Y %I:%M %p")
        self.cell(0, 5, f'Proforma N: {num_proforma}', 0, 1, 'R')
        self.cell(0, 5, f'Fecha: {fecha_hoy}', 0, 1, 'R')
        self.ln(10)

def generar_pdf(datos_cliente, items, info_adicional, aplicar_iva):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, "GRUAS MAU - SERVICIO 24/7", 0, 1)
        pdf.set_font("Arial", size=9)
        pdf.cell(0, 5, "Telefonos: 8875-5921 / 6231-2471 / 8438-2706", 0, 1)
        pdf.cell(0, 5, "Emails: Mau27@gmail.com / Jossimedra@gmail.com", 0, 1)
        pdf.ln(10)

        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 7, " DATOS DEL CLIENTE", 0, 1, 'L', True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 7, f"Empresa/Nombre: {datos_cliente['nombre']}", 0, 1)
        pdf.cell(0, 7, f"Cedula: {datos_cliente['id']}", 0, 1)
        pdf.cell(0, 7, f"Telefono: {info_adicional['tel']}", 0, 1)
        pdf.ln(5)

        pdf.set_fill_color(30, 30, 30)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, " DESCRIPCION DEL SERVICIO", 1, 0, 'L', True)
        pdf.cell(25, 10, "CANT.", 1, 0, 'C', True)
        pdf.cell(35, 10, "PRECIO UNIT.", 1, 0, 'C', True)
        pdf.cell(40, 10, "TOTAL", 1, 1, 'C', True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        subtotal = 0
        for item in items:
            t_linea = item['cantidad'] * item['precio']
            # Quitar tildes para evitar errores
            desc = item['nombre'].replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n').replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            pdf.cell(90, 10, desc, 1)
            pdf.cell(25, 10, str(item['cantidad']), 1, 0, 'C')
            pdf.cell(35, 10, f"{item['precio']:,.2f}", 1, 0, 'R')
            pdf.cell(40, 10, f"{t_linea:,.2f}", 1, 1, 'R')
            subtotal += t_linea

        pdf.ln(5)
        if aplicar_iva:
            iva = subtotal * 0.13
            total = subtotal + iva
            pdf.cell(150, 8, "SUBTOTAL: ", 0, 0, 'R')
            pdf.cell(40, 8, f"{subtotal:,.2f}", 1, 1, 'R')
            pdf.cell(150, 8, "IVA (13%): ", 0, 0, 'R')
            pdf.cell(40, 8, f"{iva:,.2f}", 1, 1, 'R')
        else:
            total = subtotal
        
        pdf.set_fill_color(255, 215, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(150, 10, "TOTAL A PAGAR: ", 0, 0, 'R')
        pdf.cell(40, 10, f"{total:,.2f}", 1, 1, 'R', True)

        return pdf.output()
    except Exception as e:
        return str(e)

# --- INTERFAZ ---
st.title("🚜 Grúas Mau - Facturación")

# Es vital usar 'key' para que el sistema pueda borrarlos
with st.expander("📝 Datos del Cliente", expanded=True):
    nom = st.text_input("Empresa / Nombre", key="k_nom")
    ced = st.text_input("Cédula o NIT", key="k_ced")
    tel = st.text_input("Teléfono", key="k_tel")

st.divider()
aplicar_iva = st.checkbox("¿Cobrar el 13% de IVA?", value=False, key="k_iva")

st.subheader("🛠️ Detalle del Servicio")
it_n = st.text_input("¿Qué servicio se realizó?", key="k_desc")
c1, c2 = st.columns(2)
with c1: it_c = st.number_input("Cantidad", min_value=1, value=1, key="k_cant")
with c2: it_p = st.number_input("Precio", min_value=0.0, step=1000.0, key="k_prec")

if st.button("➕ AGREGAR A LA TABLA", use_container_width=True):
    if 'lista' not in st.session_state: st.session_state.lista = []
    st.session_state.lista.append({"nombre": it_n, "cantidad": it_c, "precio": it_p})
    st.toast("Agregado")

if 'lista' in st.session_state and st.session_state.lista:
    st.table(st.session_state.lista)
    
    res = generar_pdf({"nombre": nom, "id": ced}, st.session_state.lista, {"tel": tel}, aplicar_iva)
    
    if not isinstance(res, str):
        nom_arch = nom.replace(" ", "_") if nom else "Mau"
        st.download_button(
            label="💾 DESCARGAR PROFORMA PDF",
            data=bytes(res),
            file_name=f"Proforma_{nom_arch}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# Este botón ahora limpia TODA la memoria de la página
if st.button("🧹 LIMPIAR TODO Y NUEVA PROFORMA", use_container_width=True):
    reiniciar_aplicacion()
