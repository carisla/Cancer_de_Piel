import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta
import requests
import time
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SIGEL Pacasmayo Pro", page_icon="🏛️", layout="wide")

# Cargar secretos
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    N8N_WEBHOOK = st.secrets["N8N_WEBHOOK_WHATSAPP"]
except:
    st.error("❌ Configura .streamlit/secrets.toml")
    st.stop()

db = create_client(SUPABASE_URL, SUPABASE_KEY)

# Estilos CSS
st.markdown("""
    <style>
    .header-muni {background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%); padding: 25px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .profile-card {background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;}
    .success-text {color: #166534; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR PDF PREMIUM ---

def generar_pdf_premium(datos):
    """Genera una Licencia con diseño de Alta Seguridad"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    
    # 1. Fondo de Seguridad (Marca de agua repetida)
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(45)
    c.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.5)) # Gris muy claro
    c.setFont("Helvetica-Bold", 60)
    c.drawCentredString(0, 0, "DOCUMENTO OFICIAL")
    c.restoreState()
    
    # 2. Marco Institucional
    c.setStrokeColor(colors.navy)
    c.setLineWidth(4)
    c.rect(1*cm, 1*cm, w-2*cm, h-2*cm) # Borde grueso externo
    c.setLineWidth(1)
    c.rect(1.2*cm, 1.2*cm, w-2.4*cm, h-2.4*cm) # Borde fino interno

    # 3. Encabezado
    # Logo simulado (URL placeholder)
    c.drawImage("https://img.icons8.com/color/96/peru.png", 2*cm, h-3.5*cm, width=2*cm, height=2*cm, mask='auto')
    
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(w/2, h-2.5*cm, "MUNICIPALIDAD DISTRITAL DE PACASMAYO")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h-3.0*cm, "Gerencia de Desarrollo Económico y Fiscalización")
    c.drawCentredString(w/2, h-3.5*cm, "LEY MARCO DE LICENCIA DE FUNCIONAMIENTO N° 28976")
    
    c.setLineWidth(2)
    c.line(2*cm, h-4*cm, w-2*cm, h-4*cm)

    # 4. Título Principal
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(colors.navy)
    c.drawCentredString(w/2, h-6*cm, "LICENCIA DE FUNCIONAMIENTO")
    
    # Tipo de Licencia
    c.setFillColor(colors.white)
    c.roundRect(w/2 - 4*cm, h-7.5*cm, 8*cm, 1*cm, 10, fill=1, stroke=0) # Pastilla de fondo
    c.setFillColor(colors.red) # Cambiamos a rojo para el texto
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-7.3*cm, "DEFINITIVA")

    # 5. Cuerpo de Datos (Tabla Simulada)
    y = h - 9.5*cm
    x_lbl = 2.5*cm
    x_val = 8*cm
    
    datos_print = [
        ("N° EXPEDIENTE:", datos['codigo']),
        ("RESOLUCIÓN:", f"GDE-{random.randint(100,999)}-2025/MDP"),
        ("RAZÓN SOCIAL:", datos['propietario']),
        ("DNI / RUC:", datos.get('dni_ruc', 'No registrado')),
        ("NOMBRE COMERCIAL:", datos['comercial']),
        ("DIRECCIÓN:", datos['direccion']),
        ("GIRO AUTORIZADO:", datos['giro']),
        ("ZONIFICACIÓN:", datos['zona']),
        ("ÁREA TOTAL:", f"{datos['area']} m²"),
        ("CAPACIDAD:", f"{int(float(datos['area'])/1.5)} Personas (Aforo)")
    ]

    for label, valor in datos_print:
        c.setFillColor(colors.gray)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_lbl, y, label)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(x_val, y, str(valor))
        
        # Línea separadora sutil
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(x_lbl, y-0.2*cm, w-2.5*cm, y-0.2*cm)
        
        y -= 1.0*cm

    # 6. Sección ITSE (Caja destacada)
    c.setStrokeColor(colors.darkgreen)
    c.setLineWidth(2)
    c.roundRect(2*cm, 4*cm, w-4*cm, 2.5*cm, 10, stroke=1, fill=0)
    
    c.setFillColor(colors.darkgreen)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, 5.8*cm, "CERTIFICADO DE INSPECCIÓN TÉCNICA (ITSE)")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(w/2, 5.0*cm, f"Certificado N° {random.randint(1000,9999)}  -  Riesgo: {datos.get('riesgo', 'EVALUADO')}")
    c.drawCentredString(w/2, 4.5*cm, f"VIGENCIA HASTA: {datos['vence_itse']}")

    # 7. QR y Firmas
    # QR Placeholder (cuadro negro)
    c.setFillColor(colors.black)
    c.rect(w-5*cm, 1.5*cm, 2.5*cm, 2.5*cm)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(w-3.75*cm, 2.5*cm, "QR CODE") 
    
    # Firma
    c.setStrokeColor(colors.black)
    c.line(4*cm, 2.5*cm, 9*cm, 2.5*cm)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    c.drawCentredString(6.5*cm, 2.2*cm, "Gerente de Desarrollo Económico")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def notificar_n8n(evento, datos):
    """Envía webhook a n8n"""
    try:
        requests.post(N8N_WEBHOOK, json={"evento": evento, "datos": datos}, timeout=1)
    except:
        pass

# --- 3. NUEVO MÓDULO: GESTIÓN DE USUARIOS (ADMIN) ---

def modulo_admin_usuarios():
    st.markdown("### 👥 Gestión de Usuarios del Sistema")
    st.info("Crea cuentas para ciudadanos, cajeros o inspectores.")
    
    # Formulario de Alta
    with st.form("nuevo_usuario_form"):
        col1, col2 = st.columns(2)
        nuevo_user = col1.text_input("Usuario (Login)")
        nuevo_pass = col2.text_input("Contraseña", type="password")
        
        col3, col4 = st.columns(2)
        nuevo_nombre = col3.text_input("Nombre Completo / Razón Social")
        nuevo_rol = col4.selectbox("Rol", ["ciudadano", "cajero", "mesa_partes", "inspector_itse", "gerente"])
        
        col5, col6 = st.columns(2)
        nuevo_dni = col5.text_input("DNI / RUC")
        nuevo_tel = col6.text_input("Teléfono (WhatsApp)")
        
        if st.form_submit_button("💾 Crear Usuario"):
            if not nuevo_user or not nuevo_pass:
                st.error("Usuario y contraseña obligatorios")
            else:
                try:
                    # Validar si existe
                    check = db.table("usuarios").select("id").eq("username", nuevo_user).execute()
                    if check.data:
                        st.error("El nombre de usuario ya existe.")
                    else:
                        db.table("usuarios").insert({
                            "username": nuevo_user,
                            "password": nuevo_pass, # En prod usar hash!
                            "rol": nuevo_rol,
                            "nombre_completo": nuevo_nombre,
                            "dni_ruc": nuevo_dni,
                            "telefono": nuevo_tel
                        }).execute()
                        st.success(f"Usuario {nuevo_user} creado exitosamente.")
                except Exception as e:
                    st.error(f"Error en BD: {e}")

    st.markdown("---")
    st.markdown("#### Lista de Usuarios Activos")
    users = db.table("usuarios").select("id, username, rol, nombre_completo, telefono").execute().data
    if users:
        st.dataframe(pd.DataFrame(users))

# --- 4. NUEVO MÓDULO: MI PERFIL (CIUDADANO) ---

def modulo_mi_perfil(usuario):
    st.markdown("### 🛠️ Mi Perfil de Usuario")
    
    with st.container():
        st.markdown(f"""
        <div class="profile-card">
            <h4>{usuario['nombre_completo']}</h4>
            <p><strong>Usuario:</strong> {usuario['username']} | <strong>Rol:</strong> {usuario['rol'].upper()}</p>
        </div>
        <br>
        """, unsafe_allow_html=True)
    
    with st.form("update_profile"):
        c1, c2 = st.columns(2)
        new_email = c1.text_input("Correo Electrónico", value=usuario.get('email', ''))
        new_tel = c2.text_input("Teléfono / WhatsApp", value=usuario.get('telefono', ''))
        
        new_pass = st.text_input("Nueva Contraseña (Dejar en blanco para no cambiar)", type="password")
        
        if st.form_submit_button("🔄 Actualizar Mis Datos"):
            update_data = {
                "email": new_email,
                "telefono": new_tel
            }
            if new_pass:
                update_data["password"] = new_pass
                
            try:
                db.table("usuarios").update(update_data).eq("id", usuario['id']).execute()
                
                # Actualizar sesión para reflejar cambios
                updated_user = db.table("usuarios").select("*").eq("id", usuario['id']).execute().data[0]
                st.session_state.usuario = updated_user
                
                st.success("Datos actualizados correctamente.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error("Error al actualizar.")

# --- 5. LOGICA EXISTENTE ADAPTADA ---

def modulo_ciudadano_tramites(usuario):
    # (Lógica resumida del código anterior para trámites)
    tab1, tab2 = st.tabs(["📄 Nueva Solicitud", "📂 Mis Trámites"])
    with tab1:
        with st.form("anexo1"):
            c1, c2 = st.columns(2)
            comercial = c1.text_input("Nombre Comercial")
            giro = c2.text_input("Giro")
            direccion = st.text_input("Dirección")
            area = st.number_input("Área m2", min_value=1)
            
            if st.form_submit_button("Enviar"):
                codigo = f"EXP-{random.randint(1000,9999)}"
                db.table("expedientes").insert({
                    "usuario_id": usuario['id'], "codigo_expediente": codigo,
                    "nombre_comercial": comercial, "giro_negocio": giro,
                    "direccion": direccion, "area_m2": area, "estado": "RECIBIDO"
                }).execute()
                st.success("Enviado")
                notificar_n8n("nuevo_expediente", {"codigo": codigo, "telefono": usuario['telefono']})
    with tab2:
        mis_exp = db.table("expedientes").select("*").eq("usuario_id", usuario['id']).execute().data
        if mis_exp:
            st.dataframe(pd.DataFrame(mis_exp))

# --- 6. CONTROLADOR PRINCIPAL ---
def main():
    # Login Screen
    if 'usuario' not in st.session_state:
        st.markdown("<div class='header-muni'><h1>🏛️ SIGEL PACASMAYO</h1></div>", unsafe_allow_html=True)
        
        # --- CORRECCIÓN AQUÍ ---
        # Antes decía: c1, c2, c3 = st.columns(...)
        # Y luego usabas: with col2: (Error)
        
        col1, col2, col3 = st.columns([1,1,1]) # Ahora las variables se llaman col1, col2, col3
        
        with col2: # Ahora sí funciona porque coincide el nombre
            with st.form("login_form"):
                st.markdown("### Iniciar Sesión")
                u = st.text_input("Usuario")
                p = st.text_input("Contraseña", type="password")
                
                if st.form_submit_button("Ingresar"):
                    try:
                        # LOGIN REAL CONTRA BASE DE DATOS
                        res = db.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                        if res.data:
                            st.session_state.usuario = res.data[0]
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos")
                    except:
                        st.error("Error de conexión con BD")
            st.info("Nota: Si eres nuevo, pide al admin que te cree una cuenta.")

    else:
        # Dashboard Logueado
        user = st.session_state.usuario
        rol = user['rol']
        
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Escudo_de_Pacasmayo.png/180px-Escudo_de_Pacasmayo.png", width=80)
            st.write(f"Hola, **{user['nombre_completo']}**")
            st.caption(f"Rol: {rol.upper()}")
            
            menu = []
            if rol == 'ciudadano':
                menu = ["Mis Trámites", "Mi Perfil"]
            elif rol == 'gerente': # Admin
                menu = ["Gestión Usuarios", "Emitir Licencias"]
            # Puedes agregar más roles aquí (cajero, etc.)
            
            opcion = st.radio("Menú", menu)
            
            st.markdown("---")
            if st.button("Cerrar Sesión"):
                del st.session_state.usuario
                st.rerun()

        # Ruteo de Vistas
        if rol == 'ciudadano':
            if opcion == "Mis Trámites":
                modulo_ciudadano_tramites(user)
            elif opcion == "Mi Perfil":
                modulo_mi_perfil(user)
        
        elif rol == 'gerente':
            if opcion == "Gestión Usuarios":
                modulo_admin_usuarios()
            elif opcion == "Emitir Licencias":
                # Botón de prueba para el PDF
                if st.button("Prueba Generar PDF Premium"):
                    pdf_data = generar_pdf_premium({
                        "codigo": "EXP-PRUEBA",
                        "propietario": "JUAN PEREZ S.A.C.",
                        "dni_ruc": "20123456789",
                        "comercial": "POLLERIA EL REY",
                        "direccion": "AV. LIMA 123",
                        "giro": "RESTAURANTE",
                        "zona": "COMERCIAL",
                        "area": "120",
                        "vence_itse": "12/12/2026"
                    })
                    st.download_button("Descargar PDF Pro", pdf_data, "licencia_pro.pdf")

if __name__ == "__main__":
    main()