import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA v2026", layout="wide")
st.title("🦅 BUNKER ALPHA: Terminal de Decisión")

with st.sidebar:
    st.header("🔑 Configuración")
    openai_key = st.text_input("OpenAI API Key", type="password")
    google_key = st.text_input("Google API Key", type="password")

# --- CONSTITUCIÓN ALPHA ---
PROMPT_MADRE = """
Actúa como Scout de Élite. Tu objetivo es detectar momentum y fuego.
REGLA DE ORO: No escribas párrafos. No hagas introducciones.
FORMATO DE SALIDA (ESTRICTO):
1. Oportunidad: [Sí/No]
2. Fundamento: [Máximo 15 palabras sobre el momentum/sangre]
3. Urgencia: [Baja/Media/Alta]
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
                # Usamos el modelo Flash que ya vimos que funciona en tu cuenta
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Inyectamos la Constitución y los datos
                response = model.generate_content(PROMPT_MADRE + "\nDATOS DEL PARTIDO:\n" + raw_data)
                
                # Mostramos la respuesta con estilo limpio
                st.success(response.text)
            except Exception as e:
                st.error(f"Error en Scout: {str(e)}")

        with col2:
            st.subheader("🛡️ Auditor (ChatGPT)")
            if not openai_key:
                st.warning("⚠️ Requiere saldo en OpenAI ($5).")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Auditor de riesgo. Máximo 20 palabras."},
                                  {"role": "user", "content": raw_data}]
                    )
                    st.info(res.choices[0].message.content)
                except:
                    st.error("❌ Auditor sin saldo o desconectado.")

st.markdown("---")
st.caption("The Boss: Ejecución de élite - Proceso sobre Resultado.")
