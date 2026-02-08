import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA v2.1 - SNIPER", layout="wide")
st.title("🦅 BUNKER ALPHA: Modo Sniper")

with st.sidebar:
    st.header("🔑 Llaves de Acceso")
    openai_key = st.text_input("OpenAI API Key (Auditor)", type="password")
    google_key = st.text_input("Google API Key (Scout)", type="password")
    st.markdown("---")
    st.info("🎯 ESTRATEGIA: Crecimiento Compuesto (EV+)")

# --- CONSTITUCIÓN ALPHA v2.1 (Gobernanza Madre + Modo Sniper) ---
CONSTITUCION_ALPHA = """
[ROL] Actúas en un Comité de Decisión de Trading con IQ 228. Tu objetivo no es acertar goles, es identificar operaciones repetibles EV+.

[REGLAS SNIPER & FILTROS]
1. Ritmo Alpha: AP >= 1.2/min (Mínimo).
2. MODO SNIPER: Si AP/Min >= 1.5 Y SOT >= 4 en los últimos 15 min. Etiquetar como "🟢 SNIPER DETECTADO".
3. REGLAS INFLEXIBLES: Anti-Ravenna (Ligas Pro únicamente), Puntería (Remates Fuera < 2x SOT), Marcador (No entrar si diferencia > 2 goles, salvo asedio 2.0 AP/min).

[FILOSOFÍA DEL COMITÉ]
- Proceso > Resultado.
- Timing de mercado obligatorio.
- El desacuerdo entre agentes es información, no error.
"""

# Instrucción específica para el Scout
SCOUT_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Scout de Oportunidad (Agresivo). Busca presión y momentum.
FORMATO DE SALIDA (ESTRICTO):
1. Oportunidad detectada: [SÍ/NO/🟢 SNIPER]
2. Fundamento principal: [1 línea de alto impacto]
3. Nivel de urgencia: [Baja/Media/Alta]
---
🔍 ANÁLISIS TÉCNICO: [Máximo 3 puntos clave]
"""

# Instrucción específica para el Auditor
AUDITOR_PROMPT = CONSTITUCION_ALPHA + """
TU ROL: Auditor de Riesgo (Conservador). Evalúa contexto y gestión de capital.
FORMATO DE SALIDA (ESTRICTO):
1. Veredicto: [SÍ/NO/ESPERAR]
2. Riesgo clave: [1 línea de por qué NO operar]
3. Daño potencial: [Bajo/Medio/Alto]
---
🛡️ GESTIÓN: [Define si es P1, P2, P3 o PRU basado en el riesgo]
"""

raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=200, placeholder="Pega las estadísticas del partido aquí...")

if st.button("⚡ EJECUTAR ANÁLISIS ALPHA"):
    if not google_key:
        st.error("❌ Falta la llave del Scout (Google).")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🦅 Scout (Oportunidad)")
            try:
                genai.configure(api_key=google_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content(SCOUT_PROMPT + "\nDATOS DEL PARTIDO:\n" + raw_data)
                st.success(response.text)
            except Exception as e:
                st.error(f"Error en Scout: {str(e)}")

        with col2:
            st.subheader("🛡️ Auditor (Riesgo)")
            if not openai_key:
                st.info("⌛ Esperando saldo para activar Auditoría...")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": AUDITOR_PROMPT}, {"role": "user", "content": raw_data}]
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error("❌ Error de saldo o conexión en OpenAI.")

st.markdown("---")
st.caption("The Boss: Ejecución de élite. Proceso > Resultado.")
