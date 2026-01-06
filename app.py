import streamlit as st
import google.generativeai as genai
import os

# --- INSTRUCTIONS ---
# 1. Paste your API Key below where it says "PASTE_KEY_HERE"
# 2. Run this script.
# 3. It will print the EXACT model names you are allowed to use.

st.title("🔑 API Key Diagnostic Tool")

# Get API Key from Sidebar or Secrets
api_key = st.text_input("Enter API Key to Test:", type="password")

if st.button("Test Key Permissions"):
    if not api_key:
        st.error("Please enter a key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            st.info("📡 Contacting Google...")
            
            # 1. Ask Google for available models
            models = list(genai.list_models())
            
            st.success("✅ Connection Successful! Here is what your key can see:")
            
            found_any = False
            for m in models:
                # We only care about models that can generate text (generateContent)
                if 'generateContent' in m.supported_generation_methods:
                    found_any = True
                    st.write(f"**Model Name:** `{m.name}`")
                    st.caption(f"Description: {m.description}")
                    st.markdown("---")
            
            if not found_any:
                st.warning("⚠️ Connected, but no text-generation models found. Your key might be restricted.")
                
        except Exception as e:
            st.error("❌ CRITICAL FAILURE")
            st.error(f"Error Message: {e}")
            st.markdown("""
            **What this error means:**
            * **403 / Invalid API Key:** The key is typed wrong.
            * **404:** Your Python library is too old. UPDATE `requirements.txt`.
            * **429:** You have zero quota left. Use a different Google Account.
            """)
