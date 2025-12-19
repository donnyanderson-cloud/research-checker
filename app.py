import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AP Research IRB Auto-Checker", page_icon="📝", layout="wide")

# --- SIDEBAR: LOGO & CONFIG ---
with st.sidebar:
    # Option A: Display logo in the sidebar
    # Replace 'logo.png' with your actual filename
    st.image("BCS_blue (1).png", width=200) 
   
    # ... (rest of your sidebar code)

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    
    # Check if the key is in Secrets (Hidden Mode)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ District License Active")
    else:
        # Fallback: Ask user for key if not in secrets
        api_key = st.text_input("Enter Google API Key", type="password")
        st.info("Get a free key at aistudio.google.com")

    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Select the documents you have ready.
    2. Upload PDFs or paste text.
    3. Click 'Run Compliance Check'.
    """)
    st.warning("🔒 **Privacy:** Do not upload files containing real participant names or PII.")

# --- MAIN TITLE ---
st.title("🛡️ AP Research IRB Self-Check Tool")
st.markdown("""
This tool screens your research documents against **Blount County Policy 6.4001**, **AP Data Standards**, and **Federal Ethics Rules**.
""")
st.caption("⚠️ **Note:** This tool uses Artificial Intelligence to assist in reviewing documents. It may occasionally make errors. The final determination of ethical compliance rests with the IRB Committee, not this software.")



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

1. FATAL FLAWS (Blount County Policy 6.4001 & PPRA):
   - PROHIBITED TOPICS: Political affiliations, voting history, religious practices, firearm ownership. (Strict Fail).
   - SENSITIVE TOPICS: Mental health, sexual behavior, illegal acts, income. (Requires Parent Permission).
   - RIGHT TO INSPECT: Parent Permission forms MUST state: "Parents have the right to inspect survey materials upon request."

2. MINOR PROTECTION (OHRP / Belmont):
   - TERMINOLOGY: Minors provide 'Assent', Parents provide 'Permission'. 
   - COERCION: Participation must be VOLUNTARY. No penalty for saying no.
   - SILENCE != ASSENT: "If you don't say no, you are in" is invalid.
   - SAFETY NET: If the topic involves stress/emotions, there MUST be a "Distress Protocol" (e.g., referral to guidance counselor).

3. DATA SECURITY & INTEGRITY (AP Standards):
   - DESTRUCTION: Must state a specific DATE (e.g., May 2025) and METHOD (shred/delete).
   - ANONYMITY: If 'Anonymous', NO names/emails can be collected.
   - CONFLICT OF INTEREST: Flag if the student is surveying their own close friends, teammates, or teachers without a bias mitigation plan.

OUTPUT FORMAT:
For each document section provided, output:
- STATUS: [✅ PASS] or [❌ REVISION NEEDED]
- FINDINGS: Bullet points of specific issues found.
- ACTION: Exactly what the student needs to rewrite.
"""

# --- STEP 4: EXECUTION LOGIC (GEMINI) ---
if st.button("Run Compliance Check"):
    if not api_key:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not student_inputs:
        st.warning("Please upload or paste at least one document.")
    else:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Safety Settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
        
        # --- THE FIX IS HERE: USING GEMINI 2.0 FLASH ---
        model = genai.GenerativeModel('gemini-flash-latest', safety_settings=safety_settings)

        # Build the user message
        user_message = f"{system_prompt}\n\nAnalyze the following student documents:\n"
        for doc_type, content in student_inputs.items():
            user_message += f"\n--- {doc_type} ---\n{content[:30000]}\n" 

        with st.spinner("🤖 The AI IRB Chair is reviewing your documents..."):
            try:
                response = model.generate_content(user_message)
                
                # Display Result
                st.success("Analysis Complete!")
                st.markdown("---")
                st.markdown(response.text)
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
