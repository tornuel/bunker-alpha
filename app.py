import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BUNKER ALPHA v12.1 - ELITE ONLY", layout="wide")
st.title("🦅 BUNKER ALPHA: Sistema de Inteligencia Alpha (DUAL)")

# --- INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

with st.sidebar:
    st.header("🔑 Llaves de Mando")
    openai_key = st.text_input("OpenAI API Key (Auditor)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez)", type="password")
    
    st.markdown("---")
    st.header("⚙️ SELECCIÓN DE ARMA (SCOUT)")
    
    # --- LÓGICA DE DETECCIÓN REAL (CON FILTRO ANTI-TONTOS) ---
    modelo_google_seleccionado = None
    usar_openai_como_scout = False

    if google_key:
        try:
            genai.configure(api_key=google_key)
            # Preguntamos a Google qué hay disponible
            lista_modelos = []
            for m in genai.list_models():
                # FILTRO DE ÉLITE: SOLO ACEPTAMOS "GEMINI" Y QUE GENERE TEXTO
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini' in m.name: # <--- AQUÍ ESTÁ LA PURGA
                        lista_modelos.append(m.name)
            
            if lista_modelos:
                st.success(f"✅ ÉLITE GOOGLE: {len(lista_modelos)} modelos.")
                # Ordenamos para que los 'flash' o 'pro' salgan primero
                lista_modelos.sort(reverse=True) 
                modelo_google_seleccionado = st.selectbox(
                    "🤖 Elige tu Gemini:",
                    lista_modelos,
                    index=0
                )
            else:
                st.error("❌ Tu llave funciona, pero solo tienes modelos 'tontos' (Gemma). Pasando a OpenAI.")
                usar_openai_como_scout = True
        except Exception as e:
            st.error(f"❌ Error de conexión Google: {e}")
            usar_openai_como_scout = True
    else:
        st.warning("⚠️ Pon la Google Key para activar a Gemini.")
        usar_openai_como_scout = True

    # ACTIVACIÓN DE EMERGENCIA AUTOMÁTICA
    if usar_openai_como_scout:
        st.info("🚨 MODO EMERGENCIA: Usando OpenAI para todo.")
    
    st.markdown("---")
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
    else:
        scout_resp = ""
        auditor_resp = ""
        col1, col2 = st.columns(2)
        
        # 1. SCOUT (GOOGLE O OPENAI)
        with col1:
            st.subheader("🦅 Scout")
            # Intentamos Google si hay modelo seleccionado
            if modelo_google_seleccionado:
                try:
                    genai.configure(api_key=google_key)
                    # USAMOS EXACTAMENTE EL NOMBRE QUE GOOGLE NOS DIO EN LA LISTA
                    model_scout = genai.GenerativeModel(modelo_google_seleccionado)
                    res_scout = model_scout.generate_content(SCOUT_PROMPT + "\nDATOS:\n" + raw_data)
                    scout_resp = res_scout.text
                    st.info(f"Gemini ({modelo_google_seleccionado}):\n{scout_resp}")
                except Exception as e:
                    st.error(f"Error Gemini: {e}")
                    scout_resp = "" 
            
            # Fallback a OpenAI si Google falló o no estaba disponible
            if not scout_resp and openai_key:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_scout = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": SCOUT_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    scout_resp = res_scout.choices[0].message.content
                    st.warning(f"⚠️ Usando OpenAI como respaldo (Scout):\n{scout_resp}")
                except Exception as e:
                    st.error(f"Error OpenAI: {e}")

        # 2. AUDITOR (SIEMPRE OPENAI)
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
        if scout_resp and auditor_resp and "ERROR" not in auditor_resp:
            try:
                # El Juez usa OpenAI para máxima coherencia final
                if openai_key:
                    client = openai.OpenAI(api_key=openai_key)
                    prompt_final = JUEZ_PROMPT + f"\n\nSCOUT:\n{scout_resp}\n\nAUDITOR:\n{auditor_resp}"
                    res_juez = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "ERES EL JUEZ SUPREMO."}, {"role": "user", "content": prompt_final}]
                    )
                    juez_texto = res_juez.choices[0].message.content
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
