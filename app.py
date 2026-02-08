import streamlit as st
import openai
import google.generativeai as genai

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BUNKER ALPHA - COMITÉ", layout="wide")

st.title("🦅 BUNKER ALPHA: Dashboard de Decisión")
st.markdown("---")

# BARRA LATERAL PARA LLAVES
with st.sidebar:
    st.header("🔑 Configuración")
    openai_key = st.text_input("OpenAI API Key (Auditor)", type="password")
    google_key = st.text_input("Google API Key (Scout)", type="password")
    st.info("The Boss: Tus llaves están seguras, solo se usan en esta sesión.")

# PROMPTS DE GOBERNANZA
PROMPT_MADRE = "Actúas dentro de un Comité de Decisión en Trading Deportivo. Objetivo: Identificar operaciones EV+. Proceso > Resultado."

PROMPT_SCOUT = """Actúa como Scout de Oportunidad. Misión: Detectar momentum y fuego.
FORMATO:
Oportunidad detectada: Sí/No
Fundamento principal: 1 línea
Nivel de urgencia: Baja/Media/Alta"""

PROMPT_AUDITOR = """Actúa como Auditor de Riesgo. Misión: Proteger el bank.
FORMATO:
Veredicto: Sí/No/Esperar
Riesgo clave: 1 línea
Daño potencial al sistema: Bajo/Medio/Alto"""

# ÁREA DE DATOS
raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=150, placeholder="Marcador, Minuto, AP, SOT...")

if st.button("⚡ ANALIZAR PARTIDO"):
    if not google_key:
        st.error("❌ Falta la llave de Google Gemini.")
    elif not raw_data:
        st.warning("⚠️ Pega los datos del partido.")
    else:
        col1, col2 = st.columns(2)

        # EJECUCIÓN SCOUT (GEMINI) - CÓDIGO BLINDADO
        with col1:
            st.subheader("🦅 Scout (Gemini)")
            try:
                genai.configure(api_key=google_key)
                # Intentamos con el nombre de modelo más estándar
                model = genai.GenerativeModel('gemini-1.5-flash-latest') 
                response_scout = model.generate_content(f"{PROMPT_MADRE}\n{PROMPT_SCOUT}\nDATOS:\n{raw_data}")
                st.success(response_scout.text)
            except Exception as e:
                st.error(f"Error Gemini: {e}")

        # EJECUCIÓN AUDITOR (CHATGPT)
        with col2:
            st.subheader("🛡️ Auditor (ChatGPT)")
            if not openai_key:
                st.warning("⚠️ No hay API Key de OpenAI. Columna desactivada.")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    response_auditor = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"{PROMPT_MADRE}\n{PROMPT_AUDITOR}"},
                            {"role": "user", "content": raw_data}
                        ]
                    )
                    st.info(response_auditor.choices[0].message.content)
                except Exception as e:
                    if "insufficient_quota" in str(e):
                        st.error("❌ Error: OpenAI no tiene saldo ($0.00).")
                    else:
                        st.error(f"Error ChatGPT: {e}")

        st.markdown("---")
        st.caption("THE BOSS: Evalúa la tensión entre ambos.")
