import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
import pytz

# Configuración de página
st.set_page_config(page_title="Proforma Grúas Mau", layout="centered")
local_tz = pytz.timezone('America/Costa_Rica')

# --- INICIALIZACIÓN DE VARIABLES ---
if 'lista' not in st.session_state:
    st.session_state.lista = []
if 'form_count' not in st.session_state:
    st.session_state.form_count = 0

def limpiar_todo():
    st.session_state.lista = []
    st.session_state.form_count += 1
    st.rerun()

# Función para limpiar texto y permitir el símbolo ₡ en FPDF
def txt_pdf(texto):
    if not texto:
        return ""
    # Mantenemos ₡ y convertimos caracteres a formato seguro para FPDF
    s = str(texto).replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n').replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
    return s.encode('utf-8').decode('latin-1')

# --- CLASE PARA EL PDF ---
class PDF(FPDF):
    def header(self):
        archivo_pdf = "logo.png"
        if os.path.exists(archivo_pdf):
            self.image(archivo_pdf, 55, 10, 100) 
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

def generar_pdf(datos_cliente, datos_vehiculo, items, info_adicional, aplicar_iva, moneda_simbolo):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Emisor
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 7, "GRUAS MAU - SERVICIO 24/7", 0, 1)
        pdf.set_font("Arial", size=9)
        pdf.cell(0, 5, "Telefonos: 8875-5921 / 6231-2471 / 8438-2706", 0, 1)
        pdf.cell(0, 5, "Emails: Mau27@gmail.com / Jossimedra@gmail.com", 0, 1)
        pdf.ln(5)

        # Datos Cliente
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 7, txt_pdf(" DATOS DEL CLIENTE"), 0, 1, 'L', True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 7, txt_pdf(f"Empresa/Nombre: {datos_cliente['nombre']}"), 0, 1)
        pdf.cell(0, 7, txt_pdf(f"Nit / Cedula: {datos_cliente['id']}"), 0, 1)
        pdf.cell(0, 7, txt_pdf(f"Telefono: {info_adicional['tel']}"), 0, 1)
        pdf.ln(3)

        # Detalles del Vehículo
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 7, txt_pdf(" DETALLES DEL VEHICULO"), 0, 1, 'L', True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 7, txt_pdf(f"Vehiculo: {datos_vehiculo}"), 0, 1)
        pdf.ln(5)

        # Tabla Servicios
        pdf.set_fill_color(30, 30, 30)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, txt_pdf(" DESCRIPCION"), 1, 0, 'L', True)
        pdf.cell(20, 10, txt_pdf("CANT."), 1, 0, 'C', True)
        pdf.cell(40, 10, txt_pdf(f"PRECIO ({moneda_simbolo})"), 1, 0, 'C', True)
        pdf.cell(40, 10, txt_pdf(f"TOTAL ({moneda_simbolo})"), 1, 1, 'C', True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        subtotal = 0
        for item in items:
            t_linea = item['cantidad'] * item['precio']
            pdf.cell(90, 10, txt_pdf(item['nombre']), 1)
            pdf.cell(20, 10, str(item['cantidad']), 1, 0, 'C')
            pdf.cell(40, 10, txt_pdf(f"{moneda_simbolo} {item['precio']:,.2f}"), 1, 0, 'R')
            pdf.cell(40, 10, txt_pdf(f"{moneda_simbolo} {t_linea:,.2f}"), 1, 1, 'R')
            subtotal += t_linea

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        if aplicar_iva:
            iva = subtotal * 0.13
            total = subtotal + iva
            pdf.cell(150, 8, txt_pdf("SUBTOTAL: "), 0, 0, 'R')
            pdf.cell(40, 8, txt_pdf(f"{moneda_simbolo} {subtotal:,.2f}"), 1, 1, 'R')
            pdf.cell(150, 8, txt_pdf("IVA (13%): "), 0, 0, 'R')
            pdf.cell(40, 8, txt_pdf(f"{moneda_simbolo} {iva:,.2f}"), 1, 1, 'R')
        else:
            total = subtotal
        
        pdf.set_fill_color(255, 215, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(150, 10, txt_pdf("TOTAL A PAGAR: "), 0, 0, 'R')
        pdf.cell(40, 10, txt_pdf(f"{moneda_simbolo} {total:,.2f}"), 1, 1, 'R', True)

        return pdf.output(dest='S')
    except Exception as e:
        return str(e)

# --- INTERFAZ WEB ---
archivo_web = "logo_icono.png"
col_ico, col_tit = st.columns([1, 4])
with col_ico:
    if os.path.exists(archivo_web): st.image(archivo_web, width=70)
    else: st.write("🚜")
with col_tit:
    st.title("Grúas Mau - Facturación")

ver = st.session_state.form_count

# Moneda y configuración inicial
c_mon, c_iva = st.columns(2)
with c_mon:
    moneda_simbolo = st.radio("Tipo de Moneda", ["₡", "$"], horizontal=True, key=f"mon_{ver}")
with c_iva:
    aplicar_iva = st.checkbox("¿Cobrar 13% IVA?", value=False, key=f"iva_{ver}")

with st.expander("📝 Datos del Cliente", expanded=True):
    nom = st.text_input("Empresa / Nombre", key=f"n_{ver}")
    ced = st.text_input("Nit / Cedula", key=f"c_{ver}")
    tel = st.text_input("Telefono", key=f"t_{ver}")

st.subheader("🚗 Detalles del Vehículo")
vehiculo = st.text_input("Marca, modelo o placa", placeholder="Ej: Toyota Hilux - Placa 123456", key=f"v_{ver}")

st.divider()
st.subheader("🛠️ Detalle del Servicio")
it_n = st.text_input("¿Qué servicio se realizó?", key=f"serv_{ver}")
c1, c2 = st.columns(2)
with c1: it_c = st.number_input("Cantidad", min_value=1, value=1, key=f"cant_{ver}")
with c2: it_p = st.number_input(f"Precio Unitario ({moneda_simbolo})", min_value=0.0, step=500.0, key=f"prec_{ver}")

if st.button("➕ AGREGAR A LA TABLA", use_container_width=True):
    if it_n:
        st.session_state.lista.append({"nombre": it_n, "cantidad": it_c, "precio": it_p})
        st.toast("Servicio agregado")
    else:
        st.error("Falta descripción del servicio")

if st.session_state.lista:
    st.table(st.session_state.lista)
    
    res = generar_pdf({"nombre": nom, "id": ced}, vehiculo, st.session_state.lista, {"tel": tel}, aplicar_iva, moneda_simbolo)
    
    if isinstance(res, str) and not res.startswith("%PDF"):
        st.error(f"Error generando PDF: {res}")
    else:
        pdf_bytes = res.encode('latin-1') if isinstance(res, str) else res
        nom_arch = nom.replace(" ", "_") if nom else "Mau"
        st.download_button(
            label=f"💾 DESCARGAR PROFORMA ({moneda_simbolo})",
            data=pdf_bytes,
            file_name=f"Proforma_{nom_arch}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    if st.button("🧹 NUEVA PROFORMA (BORRAR TODO)", use_container_width=True):
        limpiar_todo()
