import streamlit as st
import google.generativeai as genai

st.title("Debug Mode")

# Get key from secrets
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

if st.button("List Available Models"):
    try:
        st.write("Checking available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.write(f"- **{m.name}**")
    except Exception as e:
        st.error(f"Error: {e}")
