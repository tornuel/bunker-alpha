import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA", layout="wide")
st.title("🦅 BUNKER ALPHA: Terminal de Decisión")

with st.sidebar:
    st.header("🔑 Configuración")
    openai_key = st.text_input("OpenAI API Key", type="password")
    google_key = st.text_input("Google API Key", type="password")

PROMPT_MADRE = "Actúas como Scout de Trading. Objetivo: Identificar presión y momentum. Proceso > Resultado."
PROMPT_FORMATO = "\nResponde en 3 líneas: 1. Oportunidad (Sí/No), 2. Fundamento, 3. Urgencia."

raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=150)

if st.button("⚡ ANALIZAR PARTIDO"):
    if not google_key:
        st.error("❌ Falta la llave de Google Gemini.")
    else:
        col1, col2 = st.columns(2)

        # SECCIÓN SCOUT (INTENTANDO EL MODELO MÁS COMPATIBLE)
        with col1:
            st.subheader("🦅 Scout (Gemini)")
            try:
                genai.configure(api_key=google_key)
                # Usamos el modelo 1.5-flash, que es el estándar gratuito universal
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(PROMPT_MADRE + PROMPT_FORMATO + "\nDATOS:\n" + raw_data)
                st.success(response.text)
            except Exception as e:
                st.error(f"Error en Scout: {str(e)}")
                st.info("Prueba a crear una API Key nueva en Google AI Studio si esto persiste.")

        # SECCIÓN AUDITOR (CHATGPT)
        with col2:
            st.subheader("🛡️ Auditor (ChatGPT)")
            if not openai_key:
                st.warning("⚠️ Requiere recarga de $5 en OpenAI.")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": PROMPT_MADRE + raw_data}]
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error("❌ Auditor fuera de servicio (Revisa saldo).")

st.markdown("---")
st.caption("The Boss: Debuggeando el sistema de élite.")
