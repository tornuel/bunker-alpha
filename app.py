import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA", layout="wide")
st.title("🦅 BUNKER ALPHA: Terminal de Decisión")

with st.sidebar:
    st.header("🔑 Configuración")
    openai_key = st.text_input("OpenAI API Key", type="password")
    google_key = st.text_input("Google API Key", type="password")

PROMPT_MADRE = "Actúas dentro de un Comité de Decisión en Trading Deportivo. Proceso > Resultado."
PROMPT_SCOUT = "Actúa como Scout. Misión: Detectar momentum. Formato: Oportunidad (Sí/No), Fundamento (1 línea), Urgencia (Baja/Media/Alta)."
PROMPT_AUDITOR = "Actúa como Auditor. Misión: Proteger el bank. Formato: Veredicto (Sí/No/Esperar), Riesgo (1 línea), Daño (Bajo/Medio/Alto)."

raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=150)

if st.button("⚡ ANALIZAR PARTIDO"):
    if not google_key:
        st.error("❌ Falta la llave de Google Gemini.")
    else:
        col1, col2 = st.columns(2)

        # SECCIÓN SCOUT (GEMINI) - VERSIÓN ULTRA-ROBUSTA
        with col1:
            st.subheader("🦅 Scout (Gemini)")
            try:
                genai.configure(api_key=google_key)
                
                # Intentamos el modelo más nuevo primero
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"{PROMPT_MADRE}\n{PROMPT_SCOUT}\nDATOS:\n{raw_data}")
                    st.success(response.text)
                except Exception:
                    # Intento 2: Modelo Pro si el Flash falla
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(f"{PROMPT_MADRE}\n{PROMPT_SCOUT}\nDATOS:\n{raw_data}")
                    st.success(response.text)
                    
            except Exception as e:
                st.error(f"Error crítico en Scout: {str(e)}")
                # DIAGNÓSTICO PARA EL JEFE:
                st.warning("🔍 Diagnóstico para Gemini: Listando modelos disponibles...")
                try:
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    st.write("Tu llave tiene acceso a estos modelos:", models)
                except:
                    st.write("No se pudieron listar los modelos. Revisa si tu API Key es válida.")

        # SECCIÓN AUDITOR (CHATGPT)
        with col2:
            st.subheader("🛡️ Auditor (ChatGPT)")
            if not openai_key:
                st.warning("⚠️ Sin API Key de OpenAI ($0.00).")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": f"{PROMPT_MADRE}\n{PROMPT_AUDITOR}"},{"role": "user", "content": raw_data}]
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error Auditor: {str(e)}")

st.caption("THE BOSS: Evalúa la tensión entre el Scout y el Auditor.")
