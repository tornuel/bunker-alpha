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

# --- SCOUT PROMPT MODIFICADO PARA EXTRAER EL NOMBRE ---
SCOUT_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Scout de Oportunidad (Agresivo).
MENTALIDAD: Acelerador. Si ves asedio, propón disparo.

⚠️ INSTRUCCIÓN DE FORMATO CRÍTICA:
La PRIMERA LÍNEA de tu respuesta DEBE SER EL NOMBRE DE LOS EQUIPOS en este formato exacto:
OBJETIVO: [Equipo Local] vs [Equipo Visitante]

FORMATO DEL RESTO:
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

TU OBJETIVO ES LA SEGURIDAD TOTAL.
- Si el Auditor dijo NO y el Juez 1 dijo SÍ -> CORRIGE A "NO" (Prioridad a la seguridad).
- Si todos coinciden -> RATIFICA.
- Si hay dudas -> ESPERAR (🟡).

⚠️ FORMATO OBLIGATORIO:
SENTENCIA FINAL: [🔴 NO OPERAR / 🟡 ESPERAR / 🟢 DISPARAR]
MOTIVO: [Resumen final]
ACCIÓN: [Instrucción precisa]
"""

# --- INTERFAZ ---
with st.form(key='bunker_form'):
    raw_data = st.text_area("📥 PEGA EL RAW DATA (Ctrl + Enter):", height=200)
    submit_button = st.form_submit_button("⚡ EJECUTAR CORTE SUPREMA")

if submit_button:
    if not raw_data:
        st.warning("⚠️ Sin datos.")
    else:
        scout_resp = ""
        auditor_resp = ""
        juez1_resp = ""
        nombre_partido_detectado = "Desconocido"
        
        col1, col2 = st.columns(2)
        
        # 1. SCOUT (GOOGLE)
        with col1:
            st.subheader("🦅 Scout (Google)")
            if modelo_google_seleccionado:
                try:
                    genai.configure(api_key=google_key)
                    model_scout = genai.GenerativeModel(modelo_google_seleccionado)
                    res_scout = model_scout.generate_content(SCOUT_PROMPT + "\nDATOS:\n" + raw_data)
                    scout_resp = res_scout.text
                    
                    # --- EXTRACCIÓN INTELIGENTE DEL NOMBRE ---
                    try:
                        for linea in scout_resp.split('\n'):
                            if "OBJETIVO:" in linea:
                                nombre_partido_detectado = linea.replace("OBJETIVO:", "").strip()
                                break
                    except:
                        pass
                    
                    st.info(scout_resp)
                except Exception as e:
                    st.error(f"Error Gemini Scout: {e}")
            elif openai_key: 
                 try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_scout = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": SCOUT_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    scout_resp = res_scout.choices[0].message.content
                    
                    # Extracción fallback OpenAI
                    try:
                        for linea in scout_resp.split('\n'):
                            if "OBJETIVO:" in linea:
                                nombre_partido_detectado = linea.replace("OBJETIVO:", "").strip()
                                break
                    except:
                        pass

                    st.warning(f"⚠️ Scout (OpenAI):\n{scout_resp}")
                 except Exception as e:
                    st.error(f"Error OpenAI: {e}")

        # 2. AUDITOR (OPENAI)
        with col2:
            st.subheader("🛡️ Auditor (OpenAI)")
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

        if scout_resp and auditor_resp and "ERROR" not in auditor_resp:
            st.markdown("---")
            
            # --- JUEZ 1 (GEMINI) ---
            st.header("👨‍⚖️ JUEZ 1: TRIBUNAL PRELIMINAR (GEMINI)")
            try:
                if modelo_google_seleccionado:
                    genai.configure(api_key=google_key)
                    model_juez1 = genai.GenerativeModel(modelo_google_seleccionado)
                    prompt_j1 = JUEZ_1_PROMPT + f"\n\nSCOUT:\n{scout_resp}\n\nAUDITOR:\n{auditor_resp}"
                    res_j1 = model_juez1.generate_content(prompt_j1)
                    juez1_resp = res_j1.text
                    st.info(juez1_resp)
                else:
                    juez1_resp = "NO DISPONIBLE"
                    st.warning("Saltando Juez 1 (Google no disponible)")
            except Exception as e:
                st.error(f"Error Juez 1: {e}")
                juez1_resp = "ERROR"

            st.markdown("⬇️ _Elevando a Corte Suprema..._ ⬇️")

            # --- JUEZ 2 (OPENAI - SUPREMO) ---
            st.header("🏛️ JUEZ 2: CORTE SUPREMA (OPENAI)")
            try:
                if openai_key:
                    client = openai.OpenAI(api_key=openai_key)
                    expediente_completo = f"""
                    SCOUT (Ataque): {scout_resp}
                    AUDITOR (Riesgo): {auditor_resp}
                    JUEZ PRELIMINAR (Opinión): {juez1_resp}
                    """
                    
                    res_supremo = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "ERES LA CORTE SUPREMA. REVISA EL EXPEDIENTE COMPLETO."}, 
                            {"role": "user", "content": JUEZ_SUPREMO_PROMPT + "\n\nEXPEDIENTE:\n" + expediente_completo}
                        ]
                    )
                    texto_supremo = res_supremo.choices[0].message.content
                    
                    # VISUALIZACIÓN
                    if "🔴" in texto_supremo:
                        st.error(texto_supremo)
                    elif "🟢" in texto_supremo:
                        st.success(texto_supremo)
                    else:
                        st.warning(texto_supremo)

                    # --- GUARDADO CON HORA DE QUITO (UTC-5) Y NOMBRE REAL ---
                    hora_quito = (datetime.utcnow() - timedelta(hours=5)).strftime("%I:%M %p")

                    veredicto = "⚪"
                    if "🔴" in texto_supremo: veredicto = "🔴 NO OPERAR"
                    elif "🟡" in texto_supremo: veredicto = "🟡 ESPERAR"
                    elif "🟢" in texto_supremo: veredicto = "🟢 DISPARAR"
                    
                    st.session_state['bitacora'].append({
                        "hora": hora_quito,
                        "partido": nombre_partido_detectado, # AQUÍ ESTÁ EL NOMBRE REAL
                        "veredicto": veredicto,
                        "sentencia": texto_supremo,
                        "motivo": "Revisar expediente completo."
                    })
            except Exception as e:
                st.error(f"Error Corte Suprema: {str(e)}")
