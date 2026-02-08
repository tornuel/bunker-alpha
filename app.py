import streamlit as st
import openai
import google.generativeai as genai
from datetime import datetime, timedelta
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BUNKER ALPHA v17.1 - DYNAMIC HYDRA", layout="wide")
st.title("🦅 BUNKER ALPHA: Corte Suprema (HYDRA DINÁMICO)")

# --- INICIALIZACIÓN DE MEMORIA ---
if 'bitacora' not in st.session_state:
    st.session_state['bitacora'] = []

# --- NÚCLEO HYDRA DINÁMICO ---
def generar_respuesta_blindada(google_key, modelo_preferido, prompt):
    """
    1. Intenta con el TITULAR.
    2. Si falla, busca DINÁMICAMENTE en tu cuenta qué modelos 'Flash' o 'Pro'
       existen realmente y los usa de suplentes.
    """
    genai.configure(api_key=google_key)
    
    # 1. DEFINIR EL EJÉRCITO DE BATALLA
    lista_batalla = [modelo_preferido]
    
    # 2. RECLUTAMIENTO DE SUPLENTES (DINÁMICO)
    # Pedimos a Google la lista REAL de lo que tienes activado
    try:
        todos_los_modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Buscamos refuerzos 'Flash' (Tanques) y 'Pro' (Cerebros)
        suplentes_flash = [m for m in todos_los_modelos if "flash" in m and m != modelo_preferido]
        suplentes_pro = [m for m in todos_los_modelos if "pro" in m and m != modelo_preferido]
        
        # Orden de batalla: Titular -> Flashes -> Pros
        lista_batalla.extend(suplentes_flash)
        lista_batalla.extend(suplentes_pro)
        
    except Exception as e:
        # Si falla el reclutamiento, intentamos con nombres genéricos por si acaso
        lista_batalla.append("models/gemini-1.5-flash")
    
    errores_log = []
    
    # 3. ATAQUE EN OLEADAS
    for modelo_actual in lista_batalla:
        try:
            # INTENTO DE DISPARO
            model_instance = genai.GenerativeModel(modelo_actual)
            response = model_instance.generate_content(prompt)
            
            # ÉXITO
            texto = response.text
            
            # Diagnóstico para el usuario
            if modelo_actual == modelo_preferido:
                status = f"✅ Ejecutado por TITULAR ({modelo_actual})"
                tipo_aviso = "success"
            else:
                status = f"⚠️ TITULAR CAÍDO. Rescatado por SUPLENTE ({modelo_actual})"
                tipo_aviso = "warning"
                
            return texto, status, tipo_aviso, True
            
        except Exception as e:
            # SI FALLA, REGISTRAMOS Y PASAMOS AL SIGUIENTE
            errores_log.append(f"[{modelo_actual}]: {str(e)}")
            continue 
            
    # SI SALIMOS DEL BUCLE, ES EL FIN
    return f"Fallo Total del Sistema. Ningún modelo respondió. Reporte: {errores_log}", "❌ ERROR CRÍTICO", "error", False

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔑 Llaves de Mando")
    openai_key = st.text_input("OpenAI API Key (Auditor & Juez Supremo)", type="password")
    google_key = st.text_input("Google API Key (Scout & Juez 1)", type="password")
    
    st.markdown("---")
    st.header("⚙️ SELECCIÓN DE ARMA (TITULAR)")
    
    modelo_titular = None
    
    if google_key:
        try:
            genai.configure(api_key=google_key)
            # OBTENEMOS LA LISTA REAL PARA EL MENÚ
            lista_modelos = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    lista_modelos.append(m.name)
            
            if lista_modelos:
                st.success(f"✅ Google Conectado")
                
                # BUSCADOR INTELIGENTE
                index_favorito = 0
                for i, nombre in enumerate(lista_modelos):
                    # Prioridad: Robotics > 2.5 > Flash Latest
                    if "robotics" in nombre:
                        index_favorito = i
                        break
                    elif "2.5" in nombre and index_favorito == 0:
                        index_favorito = i
                    elif "flash-latest" in nombre and index_favorito == 0:
                        index_favorito = i

                modelo_titular = st.selectbox(
                    "🤖 Modelo Comandante:",
                    lista_modelos,
                    index=index_favorito,
                    help="Elige tu favorito. Si falla, HYDRA buscará automáticamente cualquier modelo Flash disponible en tu cuenta."
                )
            else:
                st.error("❌ Sin modelos disponibles.")
        except Exception as e:
            st.error(f"❌ Error Google: {e}")
    else:
        st.warning("⚠️ Falta Google Key.")

    st.markdown("---")
    st.success("SISTEMA: V17.1 (HYDRA DINÁMICO)")
    st.info("🎯 OBJETIVO: $6,000")
    
    # --- BITÁCORA ---
    st.markdown("---")
    if st.button("🗑️ Borrar Historial"):
        st.session_state['bitacora'] = []
        st.rerun()
    
    if len(st.session_state['bitacora']) > 0:
        st.write("---")
        st.subheader("📂 BITÁCORA DE GUERRA")
        for i, registro in enumerate(reversed(st.session_state['bitacora'])):
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

# --- INTERFAZ PRINCIPAL ---
with st.form(key='bunker_form'):
    raw_data = st.text_area("📥 PEGA EL RAW DATA (Ctrl + Enter):", height=200)
    submit_button = st.form_submit_button("⚡ EJECUTAR SISTEMA HYDRA")

if submit_button:
    if not raw_data:
        st.warning("⚠️ Sin datos.")
    else:
        scout_resp = ""
        auditor_resp = ""
        juez1_resp = ""
        nombre_partido_detectado = "Desconocido"
        
        col1, col2 = st.columns(2)
        
        # ==========================================
        # 1. SCOUT (SISTEMA HYDRA)
        # ==========================================
        with col1:
            st.subheader("🦅 Scout (Google)")
            
            if modelo_titular:
                # LLAMADA A HYDRA
                texto, status, tipo, exito = generar_respuesta_blindada(
                    google_key, modelo_titular, SCOUT_PROMPT + "\nDATOS:\n" + raw_data
                )
                
                if exito:
                    scout_resp = texto
                    # Feedback de estado
                    if tipo == "success": st.caption(status)
                    else: st.warning(status)
                    
                    st.info(scout_resp)
                    
                    # Extraer Nombre Partido
                    try:
                        for linea in scout_resp.split('\n'):
                            if "OBJETIVO:" in linea:
                                nombre_partido_detectado = linea.replace("OBJETIVO:", "").strip()
                                break
                    except:
                        pass
                else:
                    st.error(texto)
                    
            elif openai_key: # Fallback OpenAI
                 try:
                    client = openai.OpenAI(api_key=openai_key)
                    res_scout = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": SCOUT_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    scout_resp = res_scout.choices[0].message.content
                    st.warning(f"⚠️ Scout (OpenAI - Sin Google Key):\n{scout_resp}")
                 except Exception as e:
                    st.error(f"Error OpenAI: {e}")

        # ==========================================
        # 2. AUDITOR (OPENAI - SIEMPRE FIABLE)
        # ==========================================
        with col2:
            st.subheader("🛡️ Auditor (OpenAI)")
            if not openai_key:
                st.warning("⚠️ Sin OpenAI Key.")
                auditor_resp = "NO DISPON
