import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import re

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTILO INSTITUCIONAL) ---
st.set_page_config(page_title="SISTEMA DE TRADING INSTITUCIONAL", layout="wide")
st.title("🏛️ SISTEMA DE TRADING INSTITUCIONAL (V20.0 - SNIPER)")

# --- 2. INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

# --- 3. MOTOR DE INFERENCIA (HYDRA PRO - LATEST FIRST) ---
def generar_respuesta_blindada(google_key, modelo_preferido, prompt):
    genai.configure(api_key=google_key)
    
    # DEFINIR ORDEN DE BATALLA (Priority Queue)
    lista_batalla = [modelo_preferido]
    
    try:
        todos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # ESTRATEGIA: Si el usuario pidió Latest, y falla, buscamos otros PROs
        if "latest" in modelo_preferido:
             respaldo_pro = [m for m in todos if "gemini-1.5-pro" in m and "latest" not in m]
             lista_batalla.extend(respaldo_pro)
        
        # Cualquier otro modelo PRO disponible (ej: 002, o versiones estables)
        otros_pro = [m for m in todos if "pro" in m and m != modelo_preferido]
        lista_batalla.extend(otros_pro)

        # Solo en caso de catástrofe total, usamos Flash
        respaldo_flash = [m for m in todos if "flash" in m]
        lista_batalla.extend(respaldo_flash)
        
        # Eliminar duplicados manteniendo el orden
        lista_batalla = list(dict.fromkeys(lista_batalla))
    except:
        # Fallback de emergencia si la API de listado falla
        lista_batalla = [modelo_preferido, "models/gemini-1.5-pro", "models/gemini-1.5-flash"]
    
    errores_log = []
    
    # EJECUCIÓN SECUENCIAL
    for modelo_actual in lista_batalla:
        try:
            model_instance = genai.GenerativeModel(modelo_actual)
            response = model_instance.generate_content(prompt)
            texto = response.text
            
            # ÉXITO
            if modelo_actual == modelo_preferido:
                status = f"✅ EJECUTADO POR VANGUARDIA ({modelo_actual})"
                tipo_aviso = "success"
            else:
                status = f"⚠️ VANGUARDIA CAÍDA. RESPALDO ACTIVADO ({modelo_actual})"
                tipo_aviso = "warning"
                
            return texto, status, tipo_aviso, True
            
        except Exception as e:
            error_str = str(e)
            
            # MANEJO DE ERRORES ELEGANTE (CLEAN UI)
            if "429" in error_str or "Quota exceeded" in error_str:
                match = re.search(r"retry in (\d+\.?\d*)s", error_str)
                segundos_espera = float(match.group(1)) + 1 if match else 5
                
                placeholder = st.empty()
                with placeholder.container():
                    st.warning(f"⏳ Recargando API ({modelo_actual})... Espera {int(segundos_espera)}s")
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(segundos_espera / 100)
                        progress_bar.progress(i + 1)
                placeholder.empty()
                
                errores_log.append(f"[{modelo_actual}]: Rate Limit (Manejado)")
                continue 
            else:
                errores_log.append(f"[{modelo_actual}]: {error_str}")
                continue 
            
    return f"Fallo Total del Sistema. Logs: {errores_log}", "❌ ERROR CRÍTICO", "error", False

# --- 4. UI SIDEBAR ---
with st.sidebar:
    st.header("🔑 CREDENCIALES")
    openai_key = st.text_input("OpenAI API Key (Auditor & Juez Supremo)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez 1)", type="password")
    
    st.markdown("---")
    st.header("⚙️ CONFIGURACIÓN DEL MOTOR")
    
    modelo_titular = None
    
    if google_key:
        try:
            genai.configure(api_key=google_key)
            lista_modelos = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    lista_modelos.append(m.name)
            
            if lista_modelos:
                st.success(f"✅ Google Cloud: CONECTADO")
                
                # --- AUTO-SELECTOR INTELIGENTE (PRIORIDAD LATEST) ---
                index_favorito = 0
                match_found = False
                
                # 1. BUSQUEDA DE FRANCOTIRADOR: "gemini-1.5-pro-latest"
                objetivo_primario = "gemini-1.5-pro-latest"
                for i, nombre in enumerate(lista_modelos):
                    if objetivo_primario in nombre:
                        index_favorito = i; match_found = True; break 
                
                # 2. Si no está, busca el "002" (Estable potente)
                if not match_found:
                    for i, nombre in enumerate(lista_modelos):
                        if "gemini-1.5-pro-002" in nombre:
                            index_favorito = i; match_found = True; break
                
                # 3. Si no, cualquier PRO
                if not match_found:
                    for i, nombre in enumerate(lista_modelos):
                        if "gemini-1.5-pro" in nombre and "latest" not in nombre:
                            index_favorito = i; match_found = True; break

                modelo_titular = st.selectbox(
                    "🤖 Modelo Seleccionado:",
                    lista_modelos,
                    index=index_favorito,
                    help="El sistema prioriza automáticamente el modelo LATEST."
                )
            else:
                st.error("❌ Sin modelos disponibles.")
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
    else:
        st.warning("⚠️ Ingrese Google Key.")

    st.markdown("---")
    st.info("ESTADO: ACTIVO (V20.0)")
    
    st.markdown("---")
    if st.button("🗑️ Limpiar Bitácora"):
        st.session_state['bitacora'] = []
        st.rer
