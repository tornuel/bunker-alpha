import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BUNKER ALPHA v15.2 - TARGET LOCK", layout="wide")
st.title("🦅 BUNKER ALPHA: Corte Suprema (TARGET LOCK)")

# --- INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

with st.sidebar:
    st.header("🔑 Llaves de Mando")
    openai_key = st.text_input("OpenAI API Key (Auditor & Juez Supremo)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez 1)", type="password")
    
    st.markdown("---")
    st.header("⚙️ SELECCIÓN DE ARMA (SCOUT)")
    
    # --- LÓGICA DE DETECCIÓN TOTAL ---
    modelo_google_seleccionado = None
    
    if google_key:
        try:
            genai.configure(api_key=google_key)
            lista_modelos = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    lista_modelos.append(m.name)
            
            if lista_modelos:
                st.success(f"✅ Google Conectado ({len(lista_modelos)} modelos).")
                
                # BUSQUEDA INTELIGENTE DE MODELOS
                index_favorito = 0
                for i, nombre in enumerate(lista_modelos):
                    if "robotics" in nombre:
                        index_favorito = i
                        break
                    elif "flash-latest" in nombre and index_favorito == 0:
                        index_favorito = i

                modelo_google_seleccionado = st.selectbox(
                    "🤖 Scout (Google):",
                    lista_modelos,
                    index=index_favorito
                )
            else:
                st.error("❌ Llave válida, pero sin modelos.")
        except Exception as e:
            st.error(f"❌ Error Google: {e}")
    else:
        st.warning("⚠️ Falta Google Key.")

    st.markdown("---")
    st.success("SISTEMA: V15.2 (TARGET LOCK)")
    st.info("🎯 OBJETIVO: $6,000")
    
    # --- BITÁCORA MEJORADA ---
    st.markdown("---")
    if st.button("🗑️ Borrar Historial"):
        st.session_state['bitacora'] = []
        st.rerun()
    
    if len(st.session_state['bitacora']) > 0:
        st.write("---")
        st.subheader("📂 BITÁCORA DE GUERRA")
        for i, registro in enumerate(reversed(st.session_state['bitacora'])):
            # TÍTULO LIMPIO CON NOMBRE DEL PARTIDO
            titulo_log = f"#{len(st.session_state['bitacora'])-i} | {registro['hora']} | {registro['veredicto']} | {registro.get('partido', 'Desconocido')}"
            
            with st.expander(titulo_log):
                st.markdown(f"**⚽ PARTIDO:** {registro.get('partido', 'N/A')}")
                st.markdown(f"**⚖️ SENTENCIA:**\n{registro['sentencia']}")

# --- PROMPTS ---
CONSTITUCION_ALPHA = """
[ROL PRINCIPAL]
Actúan como un Comité de Decisión en Trading Deportivo de Élite con un IQ de 228.
OBJETIVO: Crecimiento compuesto del bankroll.
FILOSOFÍA: Identificar operaciones EV+ repetibles.

[PROTOCOLO DE ANÁLISIS: RAW DATA FIRST]
Fuente de verdad: TEXTO PEGADO (Raw Data).
Input Obligatorio: Marcador, Minuto, AP, SOT, Córners, Tarjetas, Cuota.

⚖️ PRINCIPIOS INQUEBRANTABLES (AUDITOR)
- Proceso > Resultado.
- Capacidad ≠ Operabilidad.
- Necesidad > Inercia.
- Timing de mercado: Buena lectura con mala cuota = NO TRADE.

🧩 ESTRUCTURA DEL COMITÉ
1. SCOUT (Agresivo): Busca momentum y asedio.
2. AUDITOR (Conservador): Evalúa riesgo y cuota.

🏛️ REGLAS TÁCTICAS
- Ritmo Alpha: AP >= 1.2/min.
- Modo Sniper: AP/Min >= 1.5 Y SOT >= 4 (últimos 15 min).
- Regla 1.50/6: Clutch Time >70' exige Ritmo > 1.50 y 6 SOT.
- VETO Puntería: Remates Fuera > 2x SOT.
- VETO Incentivo: Dominante gana por 2+ goles (salvo xG rival > 1.0).
- SWEET SPOT: Cuota > 2.10 es VALOR PURO (APROBAR). Si < 1.80 (ESPERAR).

⛔ PROHIBICIONES ABSOLUTAS:
- JAMÁS SUGERIR "ASIAN HANDICAPS".
- Solo mercados: Ganador (1X2), Goles (Over/Under), Córners.
"""

# --- SCOUT PROMPT MODIFICADO PARA EXTRA
