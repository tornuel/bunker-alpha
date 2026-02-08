import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA v2026", layout="wide")
st.title("🦅 BUNKER ALPHA: Terminal de Decisión")

with st.sidebar:
    st.header("🔑 Configuración")
    openai_key = st.text_input("OpenAI API Key", type="password")
    google_key = st.text_input("Google API Key", type="password")

# --- CONSTITUCIÓN ALPHA ACTUALIZADA ---
PROMPT_MADRE = """
Actúa como Scout de Élite. Analiza los datos con frialdad.
ESTRUCTURA DE RESPUESTA (ESTRICTA):

1. Oportunidad: [Sí/No]
2. Fundamento: [Frase corta de alto impacto]
3. Urgencia: [Baja/Media/Alta]

---
🔍 EL POR QUÉ (PROFUNDIDAD):
1. [Análisis de la métrica más crítica]
2. [Análisis del comportamiento del equipo/rojas/sustituciones]
3. [Proyección de lo que pasará en los próximos 10 minutos]
"""

raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=150)

if st.button("⚡ ANALIZAR PARTIDO"):
    if not google_key:
        st.error("❌ Falta la llave de Google Gemini.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🦅 Scout (Gemini)")
            try:
                genai.configure(api_key=google_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                
                response = model.generate_content(PROMPT_MADRE + "\nDATOS DEL PARTIDO:\n" + raw_data)
                st.success(response.text)
            except Exception as e:
                st.error(f"Error en Scout: {str(e)}")

        with col2:
            st.subheader("🛡️ Auditor (ChatGPT)")
            if not openai_key:
                st.warning("⚠️ Sin API Key de OpenAI ($5).")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Auditor de riesgo. Máximo 30 palabras sobre por qué NO entrar."},
                                  {"role": "user", "content": raw_data}]
                    )
                    st.info(res.choices[0].message.content)
                except:
                    st.error("❌ Auditor sin saldo.")

st.markdown("---")
st.caption("The Boss: Decisión basada en datos, ejecución basada en instinto.")
