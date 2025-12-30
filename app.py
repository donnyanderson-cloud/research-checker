import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BCS Research Review Portal", page_icon="🏫", layout="wide")

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. API Key Handling
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ District License Active")
    else:
        api_key = st.text_input("Enter Google API Key", type="password")
        st.info("Get a free key at aistudio.google.com")

    st.markdown("---")
    
    # 2. THE MODE SELECTOR
    st.subheader("👥 Select User Mode")
    user_mode = st.radio(
        "Who are you?",
        ["AP Research Student", "External / Higher Ed Researcher"],
        captions=["For BCS High School Students", "For University/PhD Proposals"]
    )
    
    st.markdown("---")
    st.warning("🔒 **Privacy:** Do not upload files containing real participant names or PII.")

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

# ==========================================
# MODE A: AP RESEARCH STUDENT
# ==========================================
if user_mode == "AP Research Student":
    st.title("🛡️ AP Research IRB Self-Check Tool")
    st.markdown("""
    **For BCS Students:** Screen your research documents against **Policy 6.4001** and **AP Ethics Standards**.
    """)

    # --- INPUTS ---
    document_types = [
        "Research Proposal",
        "Survey / Interview Questions",
        "Parent Permission Form",
        "Principal/District Permission Forms"
    ]
    selected_docs = st.multiselect("Select documents to screen:", document_types, default=["Research Proposal"])
    
    student_inputs = {}

    if "Research Proposal" in selected_docs:
        st.markdown("### 1. Research Proposal")
        file = st.file_uploader("Upload Proposal (PDF)", type="pdf", key="ap_prop")
        if file: student_inputs["PROPOSAL"] = extract_text(file)

    if "Survey / Interview Questions" in selected_docs:
        st.markdown("### 2. Survey or Interview Script")
        input_method = st.radio("Input Method:", ["Paste Text", "Upload PDF"], horizontal=True, key="ap_survey_toggle")
        
        if input_method == "Paste Text":
            st.info("💡 Tip: For Google Forms, Ctrl+A -> Copy -> Paste here.")
            text = st.text_area("Paste text here:", height=200, key="ap_survey_text")
            if text: student_inputs["SURVEY"] = text
        else:
            file = st.file_uploader("Upload Survey PDF", type="pdf", key="ap_survey_file")
            if file: student_inputs["SURVEY"] = extract_text(file)

    if "Parent Permission Form" in selected_docs:
        st.markdown("### 3. Parent Permission Form")
        file = st.file_uploader("Upload Parent Form (PDF)", type="pdf", key="ap_parent")
        if file: student_inputs["PARENT_FORM"] = extract_text(file)

    # --- AP SYSTEM PROMPT ---
    system_prompt = """
    ROLE: AP Research IRB Compliance Officer for Blount County Schools.
    
    CRITERIA (Policy 6.4001 & Federal Rules):
    1. PROHIBITED: Political affiliation, voting history, religious practices, firearm ownership. (Strict Fail).
    2. SENSITIVE: Mental health, sexual behavior, illegal acts, income. Requires 'Active Written Consent'.
    3. MINOR PROTECTION: Participation is VOLUNTARY. No coercion.
    4. DATA: Must have destruction date and method.
    
    OUTPUT:
    - STATUS: [✅ PASS] or [❌ REVISION NEEDED]
    - FINDINGS: Bullet points.
    - ACTION: Specific rewrite instructions.
    """

# ==========================================
# MODE B: EXTERNAL / HIGHER ED RESEARCHER
# ==========================================
else:
    st.title("🏛️ External Research Proposal Review")
    st.markdown("""
    **For University & External Researchers:** Pre-screen your proposal against **Blount County Schools Research Procedures**.
    
    *Reference: Policy 6.4001 and Administrative Procedure for Research Requests.*
    """)

    # --- INPUTS ---
    st.info("Please upload your documents for review.")
    
    external_inputs = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Main Proposal Packet")
        st.caption("Should include Purpose, Methodology, Benefit to BCS, and Logistics.")
        prop_file = st.file_uploader("Upload Full Proposal (PDF)", type="pdf", key="ext_prop")
        if prop_file: external_inputs["FULL_PROPOSAL"] = extract_text(prop_file)

    with col2:
        st.markdown("### 2. Instruments & Consents")
        st.caption("Surveys, Interview Protocols, and Parent/Guardian Consent Forms.")
        inst_file = st.file_uploader("Upload Instruments (PDF)", type="pdf", key="ext_inst")
        if inst_file: external_inputs["INSTRUMENTS"] = extract_text(inst_file)

    # --- EXTERNAL SYSTEM PROMPT ---
    # Derived from the "BCS Research Studies Procedures" document provided
    system_prompt = """
    ROLE: Research Committee Reviewer for Blount County Schools (BCS).
    
    TASK: Analyze the external research proposal against District "Regulations and Procedures for Conducting Research Studies" and Board Policy 6.4001.

    CRITICAL COMPLIANCE CHECKS:

    1. BENEFIT TO DISTRICT [cite: 5, 30]
       - The proposal MUST explicitly state a "projected value of the study to Blount County."
       - If the study is purely for the researcher's degree with no clear feedback/value to BCS, flag as "Low Priority/Educational Value".

    2. BURDEN & INSTRUCTIONAL TIME [cite: 7, 10, 26]
       - Does the study interfere with instructional time?
       - Is the time commitment (minutes per participant) clearly defined?
       - Flag "Convenience Sampling" if they just want "any students available".

    3. PROHIBITED TOPICS (Strict Ban)
       - Political affiliation / Voting history
       - Religious practices
       - Firearm ownership
       - If ANY of these are asked, result is IMMEDIATE REJECTION.

    4. SENSITIVE TOPICS (Requires Explicit Consent)
       - Mental health, sexual behavior, illegal acts, family appraisals, income.
       - If present, verify that "Written, Informed, Voluntary Signed Consent" is required from parents.

    5. MANDATORY STATEMENTS
       - Must include a statement agreeing to abide by "Blount County School Board Policy 6.4001".
       - All instruments must explicitly state that responses are "Voluntary"[cite: 32].
       - Must confirm that parents have the "Right to inspect" materials[cite: 29].
       - Anonymity: Must guarantee students/schools will not be identified in publications[cite: 27].

    OUTPUT FORMAT:
    
    ### 🚦 Executive Summary
    **Status:** [RECOMMEND FOR REVIEW] or [REVISION REQUIRED]
    
    ### 🔍 Compliance Checklist
    1. **Benefit to BCS:** [Yes/No/Unclear] - *Quote the claimed benefit.*
    2. **Prohibited Topics:** [Detected/None]
    3. **Policy 6.4001 Agreement:** [Present/Missing] - *Must explicitly mention the policy number.*
    4. **Voluntary Statement:** [Present/Missing] - *Check instruments.*
    
    ### 📝 Detailed Findings & Action Items
    * [List specific missing elements or red flags based on the citations above]
    """
    
    # Point the processing variable to the external inputs
    student_inputs = external_inputs

# ==========================================
# EXECUTION LOGIC (SHARED)
# ==========================================
if st.button("Run Compliance Check"):
    if not api_key:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not student_inputs:
        st.warning("Please upload at least one document.")
    else:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Using Flash for speed/cost
        model = genai.GenerativeModel('gemini-2.0-flash-exp') # Updated model name

        # Build message
        user_message = f"{system_prompt}\n\nAnalyze the following documents:\n"
        for doc_type, content in student_inputs.items():
            user_message += f"\n--- {doc_type} ---\n{content[:40000]}\n" 

        with st.spinner("🤖 Analyzing against District Policy..."):
            try:
                response = model.generate_content(user_message)
                st.success("Analysis Complete!")
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
