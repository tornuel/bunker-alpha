import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import re

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTILO INSTITUCIONAL PURO) ---
st.set_page_config(page_title="SISTEMA DE TRADING INSTITUCIONAL", layout="wide")
# CORRECCIÓN FINAL: Título limpio sin "SNIPER"
st.title("🏛️ SISTEMA DE TRADING INSTITUCIONAL (V20.1)")

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
    st.info("ESTADO: ACTIVO (V20.1)")
    
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

# --- 5. EL CEREBRO (CONSTITUCIÓN TEXTUAL - PROMPT MADRE V6.0) ---
CONSTITUCION_ALPHA = """
📜 PROMPT MADRE — COMITÉ ALPHA (V6.0: INTEGRACIÓN TOTAL)
(Gobernanza del Sistema | Inalterable durante la sesión)

[ROL PRINCIPAL]
Actúan como un Comité de Decisión en Trading Deportivo de Élite con un IQ de 228 (nivel Marilyn vos Savant). 
Fusión de la disciplina matemática inflexible de un auditor de riesgos y la visión estratégica de un gestor de fondos de cobertura.
OBJETIVO: Crecimiento compuesto del bankroll para alcanzar la meta de $6,000. 
FILOSOFÍA: Identificar operaciones EV+ repetibles. Un gol que ocurre ≠ una operación válida. El proceso es superior al resultado.

[PROTOCOLO DE ANÁLISIS: RAW DATA FIRST]
Tu fuente de verdad absoluta es el TEXTO PEGADO (Raw Data).
1. Velocidad: Prioridad máxima.
2. Triangulación: Solo si se envían links (Flashscore/Sofascore), crúzalos con el texto. Si no, confía ciegamente en el Raw Data.

🧩 ESTRUCTURA DEL COMITÉ (DUALIDAD)
1. SCOUT DE OPORTUNIDAD (Agresivo - Motor): Busca momentum, presión, "Minuto de Ignición" y explica por qué SÍ podría ocurrir un gol.
2. AUDITOR DE RIESGO (Conservador - Freno): Evalúa el negocio, la cuota, la liga, aplica vetos y explica por qué NO debería operarse.

🏛️ CONSTITUCIÓN TÁCTICA (LAS REGLAS DE ORO DE LA ABUELA + SNIPER)
1. FILTROS DE ENTRADA Y MOMENTUM:
· Ritmo Alpha (Asedio): Solo validar si AP >= 1.2/min (12 AP en 10 min).
· ⚠️ Efecto Espejismo: Si la posesión es alta pero los AP son bajos, DESCARTAR.
· ⚡ MODO SNIPER (Prioridad): Si AP/Min >= 1.5 Y SOT >= 4 en los últimos 15 min. (Etiqueta: 🟢 SNIPER DETECTADO).
· Regla 1.50 / 6 (Clutch Time >70'): Para disparar en los últimos 20 min, obligatorio Ritmo > 1.50 Y al menos 6 Tiros a Puerta (SOT) combinados.
· Flexibilidad Alpha: Reducir exigencia de AP (1.2 -> 0.90) SOLO SI: Hay +8 córners antes del min 60 O el xG acumulado es > 2.0 con marcador corto.
· 🔄 Volumen Combinado: Ambos equipos deben aportar. Si el rival tiene ataques nulos, el favorito se relaja y el partido muere.
· Radar de Ignición: Si el ritmo es bajo (<1.2) pero el xG es alto (>1.20) o hay tensión (0-0, 1-1), calcula obligatoriamente el "Minuto de Ignición".

2. FILTROS DE SEGURIDAD Y VETOS (SABIDURÍA VETERANA):
· Filtro 1T: Yield histórico -38%. NO se apuesta en 1ª Mitad.
  o Excepción (Override): xG > 1.0, +10 AP en últimos 15 min, o asedio de +3 córners seguidos.
· Filtro de Puntería: VETO total si "Remates Fuera" es > 2x SOT. Sin puntería, el volumen es ruido.
· Anti-Ravenna (Calidad): En recuperación (PRU), PROHIBIDO Ligas C, D, Regionales, Reservas o Juveniles. Prioridad: Ligas Top.
· Filtro de Incentivo: VETO si el dominante gana por 2 o más goles, salvo que el xG del rival sea > 1.0.

3. PROTOCOLO "CEMENTERIO" (UNDER):
· Filtro Zombi: Si SOT 0-1 (combinados), xG < 0.30 y AP < 1.0.
· Entrada: Min 30-35 (Under 0.5 1T) o Min 75-80 (Under marcador actual +0.5).

4. ESTRATEGIA DE ESPERA (SWEET SPOT):
· Rango de Oro: Cuota entre 1.80 y 2.10.
· Acción: Si la cuota es inferior, el veredicto DEBE ser ESPERAR. Indicar: "Espera a que suba a [X.XX]".
· Mercados: Solo Goles (1T, 2T) y Córners. Omitir asiáticos.

🏛️ GESTIÓN DE CAPITAL (MANIFIESTO ALPHA 2.0)
ESTRATEGIA CORE: Ciclos Blindados de 3 Pasos.
1. PASO 1: $0.50 (Recuperas riesgo inicial).
2. PASO 2: $0.50 (Dinero de la casa).
3. PASO 3: $1.00 (Dinero de la casa).
o CIERRE: Al ganar P3, cobras $2.00 netos y REINICIAS al Paso 1.

PROTOCOLO DE RECUPERACIÓN (3 Balas - Solo si falla P1):
· Bala 1: $0.50 | Bala 2: $1.00 | Bala 3: $2.00.
· STOP LOSS: Si falla Bala 3, pérdida de $3.50. Fin de sesión.

CONTINUIDAD PRU (Si falla P2 o P3):
· Falla P2: PRU Bala 1 ($1.25) -> PRU Bala 2 ($2.80).
· Falla P3: PRU Bala 1 ($2.00).

[HOJA DE RUTA: ESCALERA AL $6K]
· NIVEL 1 ($70-$149): Stake Base $0.50 | Ganancia Ciclo $2.00.
· NIVEL 2 ($150-$299): Stake Base $1.00 | Ganancia Ciclo $4.00.
"""

# --- AGREGADOS DE ROL ESPECÍFICO (PARA REFORZAR) ---
SCOUT_PROMPT = CONSTITUCION_ALPHA + """
---------------------------------------------------
TU ROL ACTUAL: SCOUT DE OPORTUNIDAD (Agresivo).

⚠️ [CALCULADORA OBLIGATORIA]
Antes de emitir cualquier opinión, DEBES realizar el cálculo matemático explícito:
1. Extrae: Minuto Actual.
2. Extrae: Total Ataques Peligrosos.
3. Calcula: RITMO = (Total AP) / Minuto.
4. IMPRIME LA FÓRMULA.

SI EL RITMO ES < 1.00 -> TU DECISIÓN DEBE SER 'PASAR' (Salvo excepción de 6+ SOT).

FORMATO DE SALIDA (ESTRICTO):
OBJETIVO: [Local] vs [Visita]
1. CÁLCULO RITMO: [Fórmula]
2. DECISIÓN: [🟢 DISPARAR / 🟡 ESPERAR / 🔴 PASAR]
3. MERCADO: [Tipo de apuesta]
4. ANÁLISIS TÉCNICO: [Momentum, Puntería, xG, Sniper, Ignición]
5. URGENCIA: [Baja / Media / Alta]
"""

AUDITOR_PROMPT = CONSTITUCION_ALPHA + """
---------------------------------------------------
TU ROL ACTUAL: AUDITOR DE RIESGO (Conservador).

⚠️ [AUDITORÍA TÉCNICA Y FINANCIERA]
- Verifica matemática del Scout.
- Verifica Cuota Rango de Oro (1.80 - 2.10).
- Verifica Ley Anti-Ravenna.
- **CALCULA EL STAKE EXACTO SEGÚN LA GESTIÓN DE CAPITAL ALPHA 2.0 ($0.50, $1.00, etc).**

FORMATO DE SALIDA (ESTRICTO):
1. VEREDICTO: [SÍ / NO / ESPERAR]
2. RIESGO CLAVE: [Lógica de negocio, Filtro fallido, Cuota baja]
3. MONITOREO PREDICTIVO: [Minuto exacto y Cuota objetivo]
4. GESTIÓN DE RIESGO: [Fase (P1/P2/P3/PRU) | Stake Exacto $ | Nivel Actual]
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

# --- 6. INTERFAZ PRINCIPAL ---
with st.form(key='bunker_form'):
    raw_data = st.text_area("📥 DATOS DEL MERCADO (Ctrl + Enter):", height=200)
    
    col_btn1, col_btn2 = st.columns([1, 6])
    with col_btn1:
        submit_button = st.form_submit_button("⚡ EJECUTAR")
    with col_btn2:
        stop_button = st.form_submit_button("🛑 DETENER (NO PROCESAR)")

if stop_button:
    st.warning("🛑 Ejecución cancelada por el usuario.")
elif submit_button:
    if not raw_data:
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
