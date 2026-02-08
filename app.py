import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BUNKER ALPHA v9.1 - DIAGNÓSTICO", layout="wide")
st.title("🦅 BUNKER ALPHA: Sistema de Inteligencia Alpha")

# --- INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

with st.sidebar:
    st.header("🔑 Llaves de Mando")
    openai_key = st.text_input("OpenAI API Key (Auditor)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez)", type="password")
    
    st.markdown("---")
    st.header("⚙️ SELECCIONA TU ARMA")
    
    # --- DIAGNÓSTICO EN TIEMPO REAL ---
    modelos_disponibles = []
    if google_key:
        try:
            genai.configure(api_key=google_key)
            # Listamos TODOS los modelos que tu cuenta permite
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponibles.append(m.name)
        except Exception as e:
            st.error(f"Error conectando con Google: {e}")
    
    if modelos_disponibles:
        # El usuario elige de la lista REAL
        modelo_seleccionado = st.selectbox("Modelos Habilitados:", modelos_disponibles, index=0)
        st.success(f"✅ Conectado a: {modelo_seleccionado}")
    else:
        st.warning("⚠️ Pon tu Google API Key para cargar los modelos.")
        modelo_seleccionado = "gemini-pro" # Fallback por si acaso

    st.info("🎯 OBJETIVO: $6,000")
    
    # --- BITÁCORA ---
    st.markdown("---")
    st.header("📂 BITÁCORA")
    if len(st.session_state['bitacora']) > 0:
        for i, registro in enumerate(reversed(st.session_state['bitacora'])):
            with st.expander(f"#{len(st.session_state['bitacora'])-i} | {registro['hora']} | {registro['veredicto']}"):
                st.write(f"**Juez:** {registro['sentencia']}")
                st.caption(f"**Motivo:** {registro['motivo']}")
    
    if st.button("🗑️ Borrar Historial"):
        st.session_state['bitacora'] = []
        st.rerun()

# --- CONSTITUCIÓN ALPHA ---
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

⛔ PROHIBICIONES ABSOLUTAS (CRÍTICO):
- JAMÁS SUGERIR "ASIAN HANDICAPS" (Hándicap Asiático).
- JAMÁS SUGERIR "DNB" (Draw No Bet).
- Solo mercados LÍQUIDOS: Ganador (1X2), Goles (Over/Under), Córners, Ambos Marcan.
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

JUEZ_PROMPT = """
ACTÚAS COMO JUEZ SUPREMO.
REGLAS:
1. Auditor NO -> 🔴 NO OPERAR.
2. Scout NO -> 🔴 NO OPERAR.
3. Scout SÍ + Auditor ESPERAR -> 🟡 ESPERAR.
4. AMBOS SÍ -> 🟢 DISPARAR.
SALIDA ÚNICA:
SENTENCIA FINAL: [🔴/🟡/🟢]
MOTIVO: [Resumen]
ACCIÓN: [Instrucción]
"""

# --- INTERFAZ ---
with st.form(key='bunker_form'):
    raw_data = st.text_area("📥 PEGA EL RAW DATA (Ctrl + Enter):", height=200)
    submit_button = st.form_submit_button("⚡ EJECUTAR SISTEMA")

if submit_button:
    if not raw_data:
        st.warning("⚠️ Sin datos.")
    elif not google_key:
        st.error("❌ Falta Google Key.")
    else:
        scout_resp = ""
        auditor_resp = ""
        col1, col2 = st.columns(2)
        
        # 1. SCOUT (CON MODELO SELECCIONADO)
        with col1:
            st.subheader("🦅 Scout")
            try:
                genai.configure(api_key=google_key)
                # Usamos el modelo que elegiste en la lista
                model_scout = genai.GenerativeModel(modelo_seleccionado)
                res_scout = model_scout.generate_content(SCOUT_PROMPT + "\nDATOS:\n" + raw_data)
                scout_resp = res_scout.text
                st.info(scout_resp)
            except Exception as e: 
                st.error(f"Error Scout: {str(e)}")
                st.warning("👉 Prueba eligiendo otro modelo de la lista izquierda.")

        # 2. AUDITOR (OpenAI)
        with col2:
            st.subheader("🛡️ Auditor")
            if not openai_key:
                st.warning("⚠️ Sin OpenAI Key.")
                auditor_resp = "NO DISPONIBLE."
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_auditor = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    auditor_resp = res_auditor.choices[0].message.content
                    st.success(auditor_resp)
                except Exception as e: 
                    st.error(f"Error OpenAI: {str(e)}")
                    auditor_resp = "ERROR."

        # 3. JUEZ
        st.markdown("---")
        st.header("⚖️ SENTENCIA")
        if scout_resp and "ERROR" not in auditor_resp:
            try:
                model_juez = genai.GenerativeModel(modelo_seleccionado)
                prompt_final = JUEZ_PROMPT + f"\n\nSCOUT:\n{scout_resp}\n\nAUDITOR:\n{auditor_resp}"
                res_juez = model_juez.generate_content(prompt_final)
                
                juez_texto = res_juez.text
                st.markdown(f"### {juez_texto}")

                # Bitácora
                veredicto = "⚪"
                if "🔴" in juez_texto: veredicto = "🔴 NO OPERAR"
                elif "🟡" in juez_texto: veredicto = "🟡 ESPERAR"
                elif "🟢" in juez_texto: veredicto = "🟢 DISPARAR"
                
                st.session_state['bitacora'].append({
                    "hora": datetime.now().strftime("%H:%M:%S"),
                    "veredicto": veredicto,
                    "sentencia": juez_texto,
                    "motivo": "Ver detalle."
                })
            except Exception as e:
                st.error(f"Error Juez: {str(e)}")
