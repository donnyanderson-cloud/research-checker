import streamlit as st
import openai
from PyPDF2 import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AP Research IRB Auto-Checker", page_icon="📝", layout="wide")

# --- SIDEBAR: API KEY & INSTRUCTIONS ---
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.markdown("---")
    st.markdown("""
    **How to use:**
    1. Enter your API Key above.
    2. Select the documents you have ready.
    3. Upload PDFs or paste text.
    4. Click 'Run Compliance Check'.
    """)
    st.warning("🔒 **Privacy:** Documents are processed in memory and are NOT saved.")

# --- MAIN TITLE ---
st.title("🛡️ AP Research IRB Self-Check Tool")
st.markdown("""
This tool screens your research documents against **Blount County Policy 6.4001**, **AP Data Standards**, and **Federal Ethics Rules**.
""")

# --- STEP 1: MULTI-SELECT INTERFACE ---
document_types = [
    "Research Proposal",
    "Survey / Interview Questions",
    "Parent Permission Form",
    "Principal/District Permission Forms"
]

selected_docs = st.multiselect(
    "Select the documents you want to screen:",
    options=document_types,
    default=["Research Proposal"]
)

# --- HELPER FUNCTION: PDF TEXT EXTRACTION ---
def extract_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- STEP 2: DYNAMIC UPLOADERS ---
student_inputs = {}

if "Research Proposal" in selected_docs:
    st.markdown("### 1. Research Proposal")
    file = st.file_uploader("Upload Proposal (PDF)", type="pdf", key="prop")
    if file:
        student_inputs["PROPOSAL"] = extract_text(file)

if "Survey / Interview Questions" in selected_docs:
    st.markdown("### 2. Survey or Interview Script")
    st.info("💡 **For Google Forms:** Open your form, press Ctrl+A (Select All), Copy, and Paste the text below.")
    survey_text = st.text_area("Paste Survey Questions Here:", height=200, key="survey")
    if survey_text:
        student_inputs["SURVEY"] = survey_text

if "Parent Permission Form" in selected_docs:
    st.markdown("### 3. Parent Permission Form")
    file = st.file_uploader("Upload Parent Form (PDF)", type="pdf", key="parent")
    if file:
        student_inputs["PARENT_FORM"] = extract_text(file)

if "Principal/District Permission Forms" in selected_docs:
    st.markdown("### 4. Administrative Permission Forms")
    file = st.file_uploader("Upload Principal/District Request (PDF)", type="pdf", key="admin")
    if file:
        student_inputs["ADMIN_FORMS"] = extract_text(file)

# --- STEP 3: THE MASTER SYSTEM PROMPT ---
system_prompt = """
ROLE:
You are the AP Research IRB Compliance Officer for Blount County Schools. Screen student research documents for ethical violations.

CRITERIA & RULES:

1. FATAL FLAWS (Blount County Policy 6.4001):
   - PROHIBITED TOPICS: Political affiliations, voting history, religious practices, firearm ownership. (Strict Fail).
   - SENSITIVE TOPICS: Mental health, sexual behavior, illegal acts, income. (Requires Parent Permission).

2. MINOR PROTECTION (OHRP / Belmont):
   - TERMINOLOGY: Minors provide 'Assent', Parents provide 'Permission'. (Students often wrongly use 'Consent' for minors).
   - COERCION: Participation must be VOLUNTARY. No penalty for saying no.
   - SILENCE != ASSENT: "If you don't say no, you are in" is invalid.

3. DATA SECURITY (AP Standards):
   - DESTRUCTION: Must state a specific DATE (e.g., May 2025) and METHOD (shred/delete).
   - ANONYMITY: If 'Anonymous', NO names/emails can be collected. If names collected, must be 'Confidential'.

OUTPUT FORMAT:
For each document section provided, output:
- STATUS: [✅ PASS] or [❌ REVISION NEEDED]
- FINDINGS: Bullet points of specific issues found.
- ACTION: Exactly what the student needs to rewrite.
"""

# --- STEP 4: EXECUTION LOGIC ---
if st.button("Run Compliance Check"):
    if not api_key:
        st.error("⚠️ Please enter an OpenAI API Key in the sidebar to proceed.")
    elif not student_inputs:
        st.warning("Please upload or paste at least one document.")
    else:
        client = openai.OpenAI(api_key=api_key)
        
        # Build the user message based ONLY on what was uploaded
        user_message = "Analyze the following student documents:\n"
        for doc_type, content in student_inputs.items():
            user_message += f"\n--- {doc_type} ---\n{content[:15000]}\n" # Limit char count per doc to prevent errors

        with st.spinner("🤖 The AI IRB Chair is reviewing your documents..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.0
                )
                
                # Display Result
                st.success("Analysis Complete!")
                st.markdown("---")
                st.markdown(response.choices[0].message.content)
            
            except Exception as e:
                st.error(f"An error occurred: {e}")