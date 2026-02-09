import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import re

# --- CONFIGURACIÓN DE PÁGINA (ESTILO INSTITUCIONAL) ---
st.set_page_config(page_title="SISTEMA DE TRADING INSTITUCIONAL", layout="wide")
st.title("🏛️ SISTEMA DE TRADING INSTITUCIONAL (V19.1)")

# --- INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

# --- MOTOR DE INFERENCIA (HYDRA PRO - CLEAN UI) ---
def generar_respuesta_blindada(google_key, modelo_preferido, prompt):
    """
    Motor V19: Prioriza modelos PRO.
    Maneja errores visualmente con barras de carga (Clean UI).
    """
    genai.configure(api_key=google_key)
    
    # 1. DEFINIR ORDEN DE BATALLA (JERARQUÍA DE ÉLITE)
    lista_batalla = [modelo_preferido]
    
    try:
        todos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if "gemini-1.5-pro-latest" in modelo_preferido:
             respaldo_pro = [m for m in todos if "gemini-1.5-pro" in m and "latest" not in m]
             lista_batalla.extend(respaldo_pro)
        
        respaldo_flash = [m for m in todos if "flash" in m]
        lista_batalla.extend(respaldo_flash)
        lista_batalla = list(dict.fromkeys(lista_batalla))
        
    except:
        lista_batalla = [modelo_preferido, "models/gemini-1.5-pro", "models/gemini-1.5-flash"]
    
    errores_log = []
    
    # 2. EJECUCIÓN SECUENCIAL
    for modelo_actual in lista_batalla:
        try:
            model_instance = genai.GenerativeModel(modelo_actual)
            response = model_instance.generate_content(prompt)
            texto = response.text
            
            if modelo_actual == modelo_preferido:
                status = f"✅ Ejecutado por MOTOR PRINCIPAL ({modelo_actual})"
                tipo_aviso = "success"
            else:
                status = f"⚠️ MOTOR PRINCIPAL CAÍDO. Respaldo activado ({modelo_actual})"
                tipo_aviso = "warning"
                
            return texto, status, tipo_aviso, True
            
        except Exception as e:
            error_str = str(e)
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
                
                errores_log.append(f"[{modelo_actual}]: Rate Limit (Esperado)")
                continue 
            else:
                errores_log.append(f"[{modelo_actual}]: {error_str}")
                continue 
            
    return f"Fallo Total del Sistema. Logs: {errores_log}", "❌ ERROR CRÍTICO", "error", False

# --- UI SIDEBAR ---
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
                
                # AUTO-SELECTOR PRO
                index_favorito = 0
                match_found = False
                for i, nombre in enumerate(lista_modelos):
                    if "gemini-1.5-pro-latest" in nombre:
                        index_favorito = i; match_found = True; break
                if not match_found:
                    for i, nombre in enumerate(lista_modelos):
                        if "gemini-1.5-pro" in nombre and "latest" not in nombre:
                            index_favorito = i; match_found = True; break
                
                modelo_titular = st.selectbox(
                    "🤖 Modelo Seleccionado:",
                    lista_modelos,
                    index=index_favorito
                )
            else:
                st.error("❌ Sin modelos disponibles.")
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
    else:
        st.warning("⚠️ Ingrese Google Key.")

    st.markdown("---")
    st.info("ESTADO: ACTIVO (V19.1)")
    
    st.markdown("---")
    if st.button("🗑️ Limpiar Bitácora"):
        st.session_state['bitacora'] = []
        st.rerun()
    
    if len(st.session_state['bitacora']) > 0:
        st.write("---")
        st.subheader("📂 HISTORIAL")
        for i, registro in enumerate(reversed(st.session_state['bitacora'])):
            titulo_log = f"#{len(st.session_state['bitacora'])-i} | {registro['hora']} | {registro['veredicto']} | {registro.get('partido', 'Desconocido')}"
            with st.expander(titulo_log):
                st.markdown(f"**⚽ EVENTO:** {registro.get('partido', 'N/A')}")
                st.markdown(f"**⚖️ SENTENCIA:**\n{registro['sentencia']}")

# --- CEREBRO DEL SISTEMA (PROMPTS V6.0) ---
CONSTITUCION_ALPHA = """
📜 PROMPT MADRE — PROTOCOLO INSTITUCIONAL (V6.0)
[ROL PRINCIPAL]
Actúan como un Comité de Decisión en Trading Deportivo de Élite con un IQ de 228. 
Fusión de la disciplina matemática inflexible de un auditor de riesgos y la visión estratégica de un gestor de fondos.
OBJETIVO: Crecimiento compuesto del bankroll. 
FILOSOFÍA: Identificar operaciones EV+ repetibles. El proceso es superior al resultado.

[PROTOCOLO DE ANÁLISIS]
Tu fuente de verdad absoluta es el TEXTO PEGADO (Raw Data).

🧩 ESTRUCTURA DEL COMITÉ
1. SCOUT (Agresivo): Busca momentum y asedio.
2. AUDITOR (Conservador): Evalúa el negocio, la cuota y aplica vetos.

🏛️ CONSTITUCIÓN TÁCTICA
1. FILTROS DE ENTRADA Y MOMENTUM:
· Ritmo Alpha (Asedio): Solo validar si AP >= 1.2/min (12 AP en 10 min).
· ⚠️ Efecto Espejismo: Si la posesión es alta pero los AP son bajos, DESCARTAR.
· ⚡ MODO SNIPER (Prioridad): Si AP/Min >= 1.5 Y SOT >= 4 en los últimos 15 min.
· Regla 1.50 / 6 (Clutch Time >70'): Para disparar en los últimos 20 min, obligatorio Ritmo > 1.50 Y al menos 6 Tiros a Puerta (SOT) combinados.
· Flexibilidad Alpha: Reducir exigencia de AP (1.2 -> 0.90) SOLO SI: Hay +8 córners antes del min 60 O el xG acumulado es > 2.0 con marcador corto.
· 🔄 Volumen Combinado: Ambos equipos deben aportar. Si el rival tiene ataques nulos, el favorito se relaja y el partido muere.
· Radar de Ignición: Si el ritmo es bajo (<1.2) pero el xG es alto (>1.20) o hay tensión (0-0, 1-1), calcula el "Minuto de Ignición".

2. FILTROS DE SEGURIDAD Y VETOS:
· Filtro 1T: Yield histórico -38%. NO se apuesta en 1ª Mitad (Salvo excepción xG > 1.0 + Asedio).
· Filtro de Puntería: VETO total si "Remates Fuera" es > 2x SOT. Sin puntería, el volumen es ruido.
· Anti-Ravenna (Calidad): En recuperación (PRU), PROHIBIDO Ligas C, D, Regionales, Reservas o Juveniles. Prioridad: Ligas Top.
· Filtro de Incentivo: VETO si el dominante gana por 2 o más goles, salvo que el xG del rival sea > 1.0.

3. PROTOCOLO "CEMENTERIO" (UNDER):
· Filtro Zombi: Si SOT 0-1 (combinados), xG < 0.30 y AP < 1.0.
· Entrada: Min 30-35 (Under 0.5 1T) o Min 75-80 (Under marcador actual +0.5).

4. ESTRATEGIA DE ESPERA (SWEET SPOT):
· Rango de Oro: Cuota entre 1.80 y 2.10.
· Acción: Si la cuota es inferior, el veredicto DEBE ser ESPERAR.
· Mercados: Solo Goles (1T, 2T) y Córners. Omitir asiáticos.
"""

SCOUT_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Scout de Oportunidad (Agresivo).
MENTALIDAD: Acelerador. Si ves asedio, propón disparo.

⚠️ [CALCULADORA OBLIGATORIA]
Antes de emitir cualquier opinión, DEBES realizar el cálculo matemático explícito:
1. Extrae: Minuto Actual.
2. Extrae: Total Ataques Peligrosos.
3. Calcula: RITMO = (Total AP) / Minuto.
4. IMPRIME LA FÓRMULA.

SI EL RITMO ES < 1.00 -> TU DECISIÓN DEBE SER 'PASAR' (Salvo excepción de 6+ SOT).

FORMATO:
OBJETIVO: [Local] vs [Visita]
1. CÁLCULO RITMO: [Fórmula]
2. DECISIÓN: [🟢 DISPARAR / 🟡 ESPERAR / 🔴 PASAR]
3. MERCADO: [Tipo]
4. ANÁLISIS: [Momentum, Puntería, xG]
5. URGENCIA: [Baja/Media/Alta]
"""

AUDITOR_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Auditor de Riesgo (Conservador).
MENTALIDAD: Freno. Protege el capital.

⚠️ [AUDITORÍA TÉCNICA]
- Verifica matemática del Scout.
- Verifica Cuota Rango de Oro (1.80 - 2.10).
- Verifica Ley Anti-Ravenna.

FORMATO:
1. VEREDICTO: [SÍ / NO / ESPERAR]
2. RIESGO: [Clave]
3. MONITOREO: [Sweet Spot]
4. GESTIÓN: [Fase | Stake]
5. DAÑO: [Nivel]
"""

JUEZ_1_PROMPT = """
ACTÚAS COMO JUEZ PRELIMINAR.
Sintetiza el conflicto. Si Auditor dice NO, tú te inclinas al NO.
OPINIÓN PRELIMINAR: [TEXTO DEL VEREDICTO] [EMOJI]
"""

JUEZ_SUPREMO_PROMPT = """
ACTÚAS COMO LA CORTE SUPREMA.
- Si Auditor dijo NO y Juez 1 dijo SÍ -> CORRIGE A "NO".
- Si todos coinciden -> RATIFICA.
- Si hay dudas -> ESPERAR (🟡).

FORMATO:
SENTENCIA FINAL: [🔴 NO OPERAR / 🟡 ESPERAR / 🟢 DISPARAR]
MOTIVO: [Resumen final]
ACCIÓN: [Instrucción precisa]
"""

# --- INTERFAZ PRINCIPAL ---
with st.form(key='bunker_form'):
    raw_data = st.text_area("📥 DATOS DEL MERCADO (Ctrl + Enter):", height=200)
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        submit_button = st.form_submit_button("⚡ EJECUTAR ANÁLISIS")
    with col_btn2:
        stop_button = st.form_submit_button("🛑 DETENER")

if submit_button:
    if stop_button:
        st.warning("🛑 Ejecución detenida por el usuario.")
    elif not raw_data:
        st.warning("⚠️ Ingrese datos para iniciar.")
    else:
        scout_resp = ""
        auditor_resp = ""
        juez1_resp = ""
        nombre_partido_detectado = "Evento Desconocido"
        
        col1, col2 = st.columns(2)
        
        # 1. SCOUT
        with col1:
            st.subheader("🦅 Scout (Google)")
            if modelo_titular:
                texto, status, tipo, exito = generar_respuesta_blindada(
                    google_key, modelo_titular, SCOUT_PROMPT + "\nDATOS DEL PARTIDO:\n" + raw_data
                )
                if exito:
                    scout_resp = texto
                    if tipo == "success": st.caption(status)
                    else: st.warning(status)
                    st.info(scout_resp)
                    try:
                        for linea in scout_resp.split('\n'):
                            if "OBJETIVO:" in linea:
                                nombre_partido_detectado = linea.replace("OBJETIVO:", "").strip()
                                break
                    except: pass
                else:
                    st.error(texto)
            elif openai_key: 
                 try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_scout = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": SCOUT_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    scout_resp = res_scout.choices[0].message.content
                    st.warning(f"⚠️ Scout (OpenAI - Backup):\n{scout_resp}")
                 except Exception as e: st.error(f"Error OpenAI: {e}")

        # 2. AUDITOR
        with col2:
            st.subheader("🛡️ Auditor (OpenAI)")
            if not openai_key:
                st.warning("⚠️ Requiere OpenAI Key.")
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
                    auditor_resp = "ERROR TÉCNICO."

        # 3. TRIBUNAL (JUECES)
        if scout_resp and auditor_resp and "ERROR" not in auditor_resp:
            st.markdown("---")
            
            # --- PAUSA TÁCTICA 5s (SEGURIDAD) ---
            with st.spinner("⏳ Enfriando motores para el Tribunal... (Pausa Táctica)"):
                time.sleep(5) 
            # ------------------------------------

            # JUEZ 1
            st.header("👨‍⚖️ JUEZ PRELIMINAR")
            if modelo_titular:
                texto_j1, status_j1, tipo_j1, exito_j1 = generar_respuesta_blindada(
                    google_key, modelo_titular, 
                    JUEZ_1_PROMPT + f"\n\nREPORTE SCOUT:\n{scout_resp}\n\nREPORTE AUDITOR:\n{auditor_resp}"
                )
                if exito_j1:
                    juez1_resp = texto_j1
                    if tipo_j1 == "success": st.caption(status_j1)
                    else: st.warning(status_j1)
                    st.info(juez1_resp)
                else:
                    juez1_resp = "NO DISPONIBLE"
                    st.error(texto_j1)
            else:
                juez1_resp = "NO DISPONIBLE"

            st.markdown("⬇️ _Elevando a Corte Suprema..._ ⬇️")

            # CORTE SUPREMA
            st.header("🏛️ CORTE SUPREMA")
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
                            {"role": "system", "content": "ERES LA CORTE SUPREMA. APLICA LA CONSTITUCIÓN ALPHA."}, 
                            {"role": "user", "content": JUEZ_SUPREMO_PROMPT + "\n\nEXPEDIENTE:\n" + expediente_completo}
                        ]
                    )
                    texto_supremo = res_supremo.choices[0].message.content
                    
                    if "🔴" in texto_supremo: st.error(texto_supremo)
                    elif "🟢" in texto_supremo: st.success(texto_supremo)
                    else: st.warning(texto_supremo)

                    # REGISTRO
                    hora_quito = (datetime.utcnow() - timedelta(hours=5)).strftime("%I:%M %p")
                    veredicto = "⚪"
                    if "🔴" in texto_supremo: veredicto = "🔴 NO OPERAR"
                    elif "🟡" in texto_supremo: veredicto = "🟡 ESPERAR"
                    elif "🟢" in texto_supremo: veredicto = "🟢 DISPARAR"
                    
                    st.session_state['bitacora'].append({
                        "hora": hora_quito,
                        "partido": nombre_partido_detectado,
                        "veredicto": veredicto,
                        "sentencia": texto_supremo
                    })
            except Exception as e:
                st.error(f"Error Corte Suprema: {str(e)}")
