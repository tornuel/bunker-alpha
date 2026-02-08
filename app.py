import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA v2.0 - QUANT TRADER", layout="wide")
st.title("🦅 BUNKER ALPHA: Sistema de Inteligencia Deportiva")

with st.sidebar:
    st.header("🔑 Llaves del Búnker")
    openai_key = st.text_input("OpenAI API Key (Auditor)", type="password")
    google_key = st.text_input("Google API Key (Scout)", type="password")
    st.markdown("---")
    st.info("NIVEL 1 ($70-$149): Stake P1 $0.50")

# --- LA CONSTITUCIÓN ALPHA (EL CEREBRO) ---
CONSTITUCION_ALPHA = """
[ROL] Socio Operativo / Senior Sports Trader. IQ 228. Objetivo: $6,000.
[FILTROS ALPHA]
- Asedio: Ritmo AP >= 1.2/min.
- Excepción Asedio: Ritmo 0.90 si +8 córners antes min 60 o xG > 2.0.
- Regla 1.50/6 (Min >70): Requiere AP > 1.50 Y SOT >= 6 combinados.
- Anti-Ravenna: No entrar si Remates Fuera > 2x SOT.
- Ligas: Solo Ligas A, B y Pro. Prohibido Regionales/Juveniles en PRU.
- 1T: Solo si xG > 1.0 o +10 AP en últimos 15 min.
"""

# --- INSTRUCCIONES ESPECÍFICAS POR AGENTE ---
SCOUT_PROMPT = CONSTITUCION_ALPHA + """
TU MISIÓN: Scout de Oportunidad. Detecta momentum y fuego.
FORMATO DE RESPUESTA:
1. DECISIÓN: [🟢 DISPARAR / 🟡 ESPERAR / 🔴 PASAR]
2. MERCADO: [Tipo de apuesta y Cuota Objetivo 1.90-2.10]
3. ANÁLISIS TÉCNICO: [AP/min, SOT, xG, Filtros Alpha aplicados]
4. MONITOREO: [Minuto de Ignición / Re-evaluación]
"""

AUDITOR_PROMPT = CONSTITUCION_ALPHA + """
TU MISIÓN: Auditor de Riesgo y Gestión de Capital (Manifiesto 2.0).
FORMATO DE RESPUESTA:
1. Veredicto de Riesgo: [Aprobado/Vetado]
2. Gestión: [Fase del Ciclo: P1, P2, P3 o Rescate/PRU]
3. Riesgo Crítico: [Por qué NO entrar o qué factor vigilar]
"""

raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=200, placeholder="Pega estadísticas de Flashscore, Sofascore o Stake aquí...")

if st.button("⚡ ANALIZAR COMITÉ ALPHA"):
    if not google_key:
        st.error("❌ Falta la llave del Scout (Google).")
    elif not raw_data:
        st.warning("⚠️ Sin datos no hay análisis.")
    else:
        col1, col2 = st.columns(2)

        # 🦅 SCOUT (GEMINI) - EJECUCIÓN CON IQ 228
        with col1:
            st.subheader("🦅 Scout (Socio Operativo)")
            try:
                genai.configure(api_key=google_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content(SCOUT_PROMPT + "\nDATOS:\n" + raw_data)
                st.success(response.text)
            except Exception as e:
                st.error(f"Error Scout: {str(e)}")

        # 🛡️ AUDITOR (CHATGPT) - GESTIÓN DE CAPITAL
        with col2:
            st.subheader("🛡️ Auditor (Guardián del Bank)")
            if not openai_key:
                st.warning("⚠️ Auditor en espera de saldo ($5).")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": AUDITOR_PROMPT},
                            {"role": "user", "content": raw_data}
                        ]
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error("❌ Error de saldo o conexión en Auditor.")

st.markdown("---")
st.caption("THE BOSS: Sistema validado. Disciplina matemática sobre emoción.")
