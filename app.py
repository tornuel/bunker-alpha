import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import re

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTILO INSTITUCIONAL COMPACTO) ---
st.set_page_config(page_title="SISTEMA DE TRADING INSTITUCIONAL", layout="wide")

# Título H3 compacto
st.markdown("### 🏛️ SISTEMA DE TRADING INSTITUCIONAL (V21.4 - FULL SYSTEM)")
st.markdown("---") 

# --- 2. INICIALIZACIÓN DE MEMORIA Y ESTADO ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

# Variable de estado para controlar el texto del input
if 'input_text_key' not in st.session_state:
    st.session_state['input_text_key'] = ""

# --- 3. MOTOR DE INFERENCIA (HYDRA: PRIORIDAD 2.5 -> 1.5) ---
def generar_respuesta_blindada(google_key, modelo_preferido, prompt):
    genai.configure(api_key=google_key)
    lista_batalla = [modelo_preferido]
    
    try:
        todos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 1. Refuerzos 2.5 PRO
        respaldo_25 = [m for m in todos if "2.5" in m and "pro" in m and m != modelo_preferido]
        lista_batalla.extend(respaldo_25)
        # 2. Refuerzos 1.5 PRO
        respaldo_15 = [m for m in todos if "1.5" in m and "pro" in m and m != modelo_preferido]
        lista_batalla.extend(respaldo_15)
        # 3. Otros PRO
        otros_pro = [m for m in todos if "pro" in m and "flash" not in m and m not in lista_batalla]
        lista_batalla.extend(otros_pro)
        # 4. Emergencia Flash
        respaldo_flash = [m for m in todos if "flash" in m]
        lista_batalla.extend(respaldo_flash)
        lista_batalla = list(dict.fromkeys(lista_batalla))
    except:
        lista_batalla = [modelo_preferido, "models/gemini-2.5-pro", "models/gemini-1.5-pro"]
    
    errores_log = []
    
    for modelo_actual in lista_batalla:
        try:
            model_instance = genai.GenerativeModel(modelo_actual)
            response = model_instance.generate_content(prompt)
            return response.text, f"✅ EJECUTADO POR VANGUARDIA ({modelo_actual})", "success", True
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
                errores_log.append(f"[{modelo_actual}]: Rate Limit")
                continue 
            else:
                errores_log.append(f"[{modelo_actual}]: {error_str}")
                continue 
            
    return f"Fallo Total. Logs: {errores_log}", "❌ ERROR CRÍTICO", "error", False

# --- 4. FUNCIONES DE LIMPIEZA ---
def clear_input():
    st.session_state["raw_input"] = "" # Esto borra el contenido del text_area

# --- 5. UI SIDEBAR ---
with st.sidebar:
    st.header("🔑 CREDENCIALES")
    openai_key = st.text_input("OpenAI API Key (Auditor & Juez Supremo)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez 1)", type="password")
    
    st.markdown("---")
    st.header("⚙️ MOTOR")
    
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
                index_favorito = 0
                match_found = False
                # Prioridad 2.5 Pro -> 1.5 Pro -> Pro
                for i, nombre in enumerate(lista_modelos):
                    if "2.5" in nombre and "pro" in nombre: index_favorito = i; match_found = True; break 
                if not match_found:
                    for i, nombre in enumerate(lista_modelos):
                        if "1.5" in nombre and "pro" in nombre: index_favorito = i; match_found = True; break
                if not match_found:
                    for i, nombre in enumerate(lista_modelos):
                        if "pro" in nombre and "vision" not in nombre: index_favorito = i; match_found = True; break

                modelo_titular = st.selectbox("🤖 Modelo:", lista_modelos, index=index_favorito)
            else:
                st.error("❌ Sin modelos.")
        except: st.error("❌ Error Conexión")
    else:
        st.warning("⚠️ Ingrese Google Key.")

    st.markdown("---")
    if st.button("🗑️ Reset Bitácora Sesión"):
        st.session_state['bitacora'] = []
        st.rerun()
    
    # --- PARCHE DE VISUALIZACIÓN DE BITÁCORA ---
    if len(st.session_state['bitacora']) > 0:
        st.markdown("---")
        st.subheader("📂 HISTORIAL (SESIÓN)")
        # Bucle inverso para mostrar lo más reciente arriba
        for i, registro in enumerate(reversed(st.session_state['bitacora'])):
            num_operacion = len(st.session_state['bitacora']) - i
            titulo_log = f"#{num_operacion} | {registro['hora']} | {registro['veredicto']}"
            
            with st.expander(titulo_log):
                st.markdown(f"**⚽ PARTIDO:** {registro.get('partido', 'Desconocido')}")
                st.markdown("**⚖️ SENTENCIA:**")
                # Mostramos solo un resumen corto para no saturar el sidebar
                st.info(registro['sentencia'])

# --- 6. EL CEREBRO (PROMPT MADRE V6.0 - CON INSTRUCCIÓN DE NOMBRE) ---
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

# AGREGADO CLAVE: INSTRUCCIÓN PARA GENERAR NOMBRE DE ARCHIVO
SCOUT_PROMPT = CONSTITUCION_ALPHA + """
---------------------------------------------------
TU ROL ACTUAL: SCOUT DE OPORTUNIDAD (Agresivo).
⚠️ [CALCULADORA OBLIGATORIA]
Calcula: RITMO = (Total AP) / Minuto. IMPRIME LA FÓRMULA.

FORMATO DE SALIDA (ESTRICTO):
1. OBJETIVO: [Local] vs [Visita]
2. ARCHIVO: [Local_vs_Visita] (Escribe solo los nombres con guiones bajos, sin espacios, sin hora, sin ligas)
3. CÁLCULO RITMO: [Fórmula]
4. DECISIÓN: [🟢 DISPARAR / 🟡 ESPERAR / 🔴 PASAR]
5. MERCADO: [Tipo de apuesta]
6. ANÁLISIS TÉCNICO: [Momentum, Puntería, xG, Sniper, Ignición]
7. URGENCIA: [Baja / Media / Alta]
"""

AUDITOR_PROMPT = CONSTITUCION_ALPHA + """
---------------------------------------------------
TU ROL ACTUAL: AUDITOR DE RIESGO (Conservador).
⚠️ [AUDITORÍA TÉCNICA Y FINANCIERA]
- Verifica matemática, Rango de Oro y Ley Anti-Ravenna.
- **CALCULA STAKE EXACTO SEGÚN ALPHA 2.0 ($0.50, $1.00, etc).**
FORMATO DE SALIDA (ESTRICTO):
1. VEREDICTO: [SÍ / NO / ESPERAR]
2. RIESGO CLAVE: [Lógica de negocio, Filtro fallido, Cuota baja]
3. MONITOREO PREDICTIVO: [Minuto exacto y Cuota objetivo]
4. GESTIÓN DE RIESGO: [Fase (P1/P2/P3/PRU) | Stake Exacto $ | Nivel Actual]
5. DAÑO: [Nivel]
"""

JUEZ_1_PROMPT = """
ACTÚAS COMO JUEZ PRELIMINAR.
OPINIÓN PRELIMINAR: [TEXTO DEL VEREDICTO] [EMOJI]
"""

JUEZ_SUPREMO_PROMPT = """
ACTÚAS COMO LA CORTE SUPREMA.
FORMATO:
SENTENCIA FINAL: [🔴 NO OPERAR / 🟡 ESPERAR / 🟢 DISPARAR]
MOTIVO: [Resumen final]
ACCIÓN: [Instrucción precisa]
"""

# --- 7. INTERFAZ PRINCIPAL ---
with st.form(key='bunker_form'):
    # Usamos st.session_state para poder borrar el contenido después
    raw_data = st.text_area("📥 DATOS DEL MERCADO (Ctrl + Enter):", height=200, key="raw_input")
    
    # AJUSTE DE COLUMNAS PARA QUE LOS BOTONES NO SE MONTEN
    col_btn1, col_btn2 = st.columns([2, 5])
    with col_btn1:
        submit_button = st.form_submit_button("⚡ EJECUTAR")
    with col_btn2:
        stop_button = st.form_submit_button("🛑 DETENER")

if stop_button:
    st.warning("🛑 Ejecución cancelada.")
elif submit_button:
    if not raw_data:
        st.warning("⚠️ Ingrese datos para iniciar.")
    else:
        scout_resp = ""
        auditor_resp = ""
        juez1_resp = ""
        nombre_partido_detectado = "Evento_Desconocido" # Valor por defecto
        
        # --- PROCESO DE ANÁLISIS ---
        col1, col2 = st.columns(2)
        
        # 1. SCOUT
        with col1:
            st.subheader("🦅 Scout")
            if modelo_titular:
                texto, status, tipo, exito = generar_respuesta_blindada(
                    google_key, modelo_titular, SCOUT_PROMPT + "\nDATOS:\n" + raw_data
                )
                if exito:
                    scout_resp = texto
                    st.caption(status)
                    st.info(scout_resp)
                    
                    # --- DETECTOR DE NOMBRE "INTELIGENTE" (USA EL CAMPO 'ARCHIVO' DEL SCOUT) ---
                    # El Scout ahora nos da el nombre limpio en la línea "ARCHIVO: ..."
                    match_archivo = re.search(r"ARCHIVO[:\s\*]+(.*)", scout_resp, re.IGNORECASE)
                    if match_archivo:
                        nombre_raw = match_archivo.group(1).strip()
                        # Limpieza final por seguridad (solo letras, numeros y guiones)
                        nombre_partido_detectado = re.sub(r'[^\w\s-]', '', nombre_raw).strip()
                    else:
                        # Fallback por si el Scout olvida el campo ARCHIVO, busca OBJETIVO
                        match_obj = re.search(r"OBJETIVO[:\s\*]+(.*)", scout_resp, re.IGNORECASE)
                        if match_obj:
                            raw_name = match_obj.group(1).strip()
                            # Convertimos espacios a guiones bajos aqui
                            nombre_partido_detectado = re.sub(r'[^\w\s-]', '', raw_name).strip().replace(' ', '_')

                else: st.error(texto)
            elif openai_key: 
                 try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_scout = client.chat.completions.create(
                        model="gpt-4o-mini", messages=[{"role": "system", "content": SCOUT_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    scout_resp = res_scout.choices[0].message.content
                    st.warning(f"⚠️ Scout (Backup OpenAI):\n{scout_resp}")
                 except Exception as e: st.error(f"Error OpenAI: {e}")

        # 2. AUDITOR
        with col2:
            st.subheader("🛡️ Auditor")
            if not openai_key:
                st.warning("⚠️ Requiere OpenAI Key.")
                auditor_resp = "NO DISPONIBLE."
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_auditor = client.chat.completions.create(
                        model="gpt-4o-mini", messages=[{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    auditor_resp = res_auditor.choices[0].message.content
                    st.success(auditor_resp)
                except Exception as e: 
                    st.error(f"Error OpenAI: {str(e)}")
                    auditor_resp = "ERROR TÉCNICO."

        # 3. TRIBUNAL
        if scout_resp and auditor_resp and "ERROR" not in auditor_resp:
            st.markdown("---")
            with st.spinner("⏳ Enfriando motores... (Pausa Táctica)"):
                time.sleep(5) 

            # Juez 1
            st.header("👨‍⚖️ JUEZ PRELIMINAR")
            if modelo_titular:
                texto_j1, status_j1, tipo_j1, exito_j1 = generar_respuesta_blindada(
                    google_key, modelo_titular, JUEZ_1_PROMPT + f"\n\nSCOUT:\n{scout_resp}\n\nAUDITOR:\n{auditor_resp}"
                )
                if exito_j1:
                    juez1_resp = texto_j1
                    st.caption(status_j1)
                    st.info(juez1_resp)
                else:
                    juez1_resp = "NO DISPONIBLE"; st.error(texto_j1)
            else: juez1_resp = "NO DISPONIBLE"

            st.markdown("⬇️ _Elevando a Corte Suprema..._ ⬇️")

            # Corte Suprema
            st.header("🏛️ CORTE SUPREMA")
            texto_supremo = ""
            try:
                if openai_key:
                    client = openai.OpenAI(api_key=openai_key)
                    expediente = f"SCOUT: {scout_resp}\nAUDITOR: {auditor_resp}\nJUEZ 1: {juez1_resp}"
                    res_supremo = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "ERES LA CORTE SUPREMA. APLICA LA CONSTITUCIÓN ALPHA."}, 
                            {"role": "user", "content": JUEZ_SUPREMO_PROMPT + "\n\nEXPEDIENTE:\n" + expediente}
                        ]
                    )
                    texto_supremo = res_supremo.choices[0].message.content
                    
                    if "🔴" in texto_supremo: st.error(texto_supremo)
                    elif "🟢" in texto_supremo: st.success(texto_supremo)
                    else: st.warning(texto_supremo)

                    # REGISTRO SESIÓN (GUARDADO EN MEMORIA)
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
            except Exception as e: st.error(f"Error Corte Suprema: {str(e)}")

            # --- GENERACIÓN DE ARCHIVO DE DESCARGA ---
            st.markdown("---")
            st.subheader("💾 GUARDAR OPERACIÓN")
            
            # Formateamos el texto completo para el TXT
            informe_completo = f"""
===================================================
FECHA Y HORA: {(datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %I:%M %p")}
EVENTO: {nombre_partido_detectado}
===================================================

[RAW DATA]
{raw_data}

---------------------------------------------------
[1] REPORTE SCOUT
{scout_resp}

---------------------------------------------------
[2] REPORTE AUDITOR
{auditor_resp}

---------------------------------------------------
[3] JUEZ PRELIMINAR
{juez1_resp}

---------------------------------------------------
[4] CORTE SUPREMA (SENTENCIA FINAL)
{texto_supremo}

===================================================
FIN DEL REPORTE
"""
            # Nombre del archivo limpio
            safe_filename = nombre_partido_detectado.strip()
            if not safe_filename: safe_filename = "Analisis_Sin_Nombre"
            
            nombre_archivo = f"{safe_filename}.txt"
            
            # BOTÓN MÁGICO: DESCARGA Y LIMPIA (Callback)
            st.download_button(
                label="📥 DESCARGAR BITÁCORA Y LIMPIAR PANTALLA",
                data=informe_completo,
                file_name=nombre_archivo,
                mime="text/plain",
                on_click=clear_input, # ESTO BORRA EL CAJÓN DE ARRIBA AL HACER CLICK
                help="Al hacer clic, se descargará el análisis y se limpiará el formulario para el siguiente partido."
            )
