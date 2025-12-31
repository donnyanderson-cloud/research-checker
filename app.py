import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini Model Checker", page_icon="🕵️")

st.title("🕵️ API & Model Diagnostics")

# 1. Get API Key
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ API Key found in Secrets")
else:
    api_key = st.text_input("Enter Google API Key", type="password")

if st.button("List Available Models"):
    if not api_key:
        st.error("Please enter an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            st.write("### 📋 Available Models for `generateContent`:")
            
            # Ask Google for the list
            found_any = False
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.code(m.name) # This prints the EXACT name you need to use
                    found_any = True
            
            if not found_any:
                st.warning("No models found. Your API key might be invalid or restricted.")
                
        except Exception as e:
            st.error(f"Error connecting to Google: {e}")
            st.info("If this fails, your 'google-generativeai' library version might be too old.")
