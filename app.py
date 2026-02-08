import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BUNKER ALPHA v14.2 - VISUAL", layout="wide")
st.title("🦅 BUNKER ALPHA: Corte Suprema (JERARQUÍA VISUAL)")

# --- INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

with st.sidebar:
    st.header("🔑 Llaves de Mando")
    openai_key = st.text_input("OpenAI API Key (Auditor & Juez Supremo)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez 1)", type="password")
    
    st.markdown("---")
    st.header("⚙️ SELECCIÓN DE ARMA (SCOUT)")
    
    # --- LÓGICA DE DETECCIÓN INTELIGENTE ---
    modelo_google_seleccionado = None
    
    if google_key:
        try:
            genai.configure(api_key=google_key)
            lista_modelos = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini' in m.name: 
                        lista_modelos.append(m.name)
            
            if lista_modelos:
                # BUSCAMOS 'FLASH-LATEST' PARA PONERLO PRIMERO
                indice_favorito = 0
                for i, nombre in enumerate(lista_modelos):
                    if "flash-latest" in nombre:
                        indice_favorito = i
                        break
                    elif "flash" in nombre and "latest" not in lista_modelos[indice_favorito]:
                         indice_favorito = i

                st.success(f"✅ Google Conectado ({len(lista_modelos)} modelos).")
                modelo_google_seleccionado = st.selectbox(
                    "🤖 Scout (Google):",
                    lista_modelos,
                    index=indice_favorito
                )
            else:
                st.error("❌ Llave válida, pero sin modelos Gemini.")
        except Exception as e:
            st.error(f"❌ Error Google: {e}")
    else:
        st.warning("⚠️ Falta Google Key.")

    st.markdown("---")
    st.success("SISTEMA: V14.2 (VISUAL)")
    st.info("🎯 OBJETIVO: $6,000")
    
    # --- BITÁCORA ---
    st.markdown("---")
    if st.button("🗑️ Borrar Historial"):
        st.session_state['bitacora'] = []
        st.rerun()
    
    if len(st.session_state['bitacora']) > 0:
        st.write("---")
        for i, registro in enumerate(reversed(st.session_state['bitacora'])):
            with st.expander(f"#{len(st.session_state['bitacora'])-i} | {registro['hora']} | {registro['veredicto']}"):
                st.write(f"**Juez:** {registro['sentencia']}")

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

SCOUT_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Scout de Oportunidad (Agresivo).
MENTALIDAD: Acelerador. Si ves asedio, propón disparo.
FORMATO:
1. DECISIÓN: [🟢 DISPARAR / 🟡 ESPERAR / 🔴 PASAR]
2. MERCADO: [Tipo de apuesta - NO ASIÁTICOS]
3. ANÁLISIS: [Momentum, Puntería, xG]
4. URGENCIA: [Baja/Media/Alta]
"""

AUDITOR_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Auditor de Riesgo (Conservador).
MENTALIDAD: Freno. Protege el capital.
FORMATO:
1. VEREDICTO: [SÍ / NO / ESPERAR]
2. RIESGO: [Clave]
3. MONITOREO: [Sweet Spot]
4. GESTIÓN: [Fase | Stake]
5. DAÑO: [Nivel]
"""

# --- PROMPTS PARA DOBLE JUZGAMIENTO ---

JUEZ_1_PROMPT = """
ACTÚAS COMO JUEZ DE PRIMERA INSTANCIA (PRE-SENTENCIA).
Tu trabajo es leer al Scout y al Auditor y emitir una OPINIÓN PRELIMINAR.
Sintetiza el conflicto. Si el Auditor dice NO, tú inclínate al NO.
TU SALIDA:
DELIBERACIÓN: [Tu análisis del conflicto]
OPINIÓN PRELIMINAR: [🟢/🟡/🔴]
"""

JUEZ_SUPREMO_PROMPT = """
ACTÚAS COMO LA CORTE SUPREMA (DECISIÓN FINAL E IRREVOCABLE).
Tu tarea es revisar el caso completo:
1. Scout (Ataque)
2. Auditor (Defensa)
3. Juez de Primera Instancia (Opinión Preliminar)

TU OBJETIVO ES LA SEGUR
