import streamlit as st
import openai
import google.generativeai as genai

st.set_page_config(page_title="BUNKER ALPHA v2026", layout="wide")
st.title("🦅 BUNKER ALPHA: Terminal de Decisión")

with st.sidebar:
    st.header("🔑 Configuración")
    openai_key = st.text_input("OpenAI API Key", type="password")
    google_key = st.text_input("Google API Key", type="password")

raw_data = st.text_area("📥 PEGA EL RAW DATA AQUÍ:", height=150)

if st.button("⚡ ANALIZAR PARTIDO"):
    if not google_key:
        st.error("❌ Falta la llave de Google Gemini.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🦅 Scout (Gemini)")
            # LISTA DE MODELOS A INTENTAR (SACADOS DE TU PROPIO DIAGNÓSTICO)
            modelos_a_probar = [
                'gemini-1.5-flash', 
                'gemini-flash-latest', 
                'gemini-1.5-pro',
                'gemini-2.0-flash',
                'gemini-pro'
            ]
            
            exito = False
            genai.configure(api_key=google_key)
            
            for nombre_modelo in modelos_a_probar:
                if exito: break
                try:
                    model = genai.GenerativeModel(nombre_modelo)
                    response = model.generate_content(f"Actúa como Scout. Analiza: {raw_data}. Formato: Oportunidad(Sí/No), Fundamento, Urgencia.")
                    st.success(f"✅ Analizado con: {nombre_modelo}")
                    st.write(response.text)
                    exito = True
                except Exception as e:
                    continue # Si falla uno, intenta el siguiente
            
            if not exito:
                st.error("❌ Ningún modelo de Gemini respondió. Revisa si tu API Key es nueva o si Google tiene restricciones en tu zona.")

        with col2:
            st.subheader("🛡️ Auditor (ChatGPT)")
            if not openai_key:
                st.warning("⚠️ Requiere saldo en OpenAI.")
            else:
                try:
                    client = openai.OpenAI(api_key=openai_key)
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": f"Auditor de riesgo: {raw_data}"}]
                    )
                    st.info(res.choices[0].message.content)
                except:
                    st.error("❌ Auditor sin conexión.")

st.caption("The Boss: Luchando contra la Matrix técnica.")
