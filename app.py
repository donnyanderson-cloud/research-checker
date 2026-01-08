import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import importlib.metadata
import random
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BCS Research Review Portal", 
    page_icon="🏫", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("⚙️ Configuration")

    # 1. THE MODE SELECTOR
    st.subheader("👥 Select User Mode")
    user_mode = st.radio(
        "Who are you?",
        ["AP Research Student", "External / Higher Ed Researcher"],
        captions=["For BCS High School Students", "For University/PhD Proposals"]
    )
    
    st.markdown("---")

    # 2. PRIVACY NOTICE
    st.warning("🔒 **Privacy:** Do not upload files containing real participant names or PII.")

    # 3. FILE NAMING GUIDE
    with st.expander("📂 File Naming Standards"):
        if user_mode == "AP Research Student":
            st.markdown("""
            **⚠️ GOOGLE DOCS USERS:**
            Please name your Google Doc using this format **before** downloading as PDF.
            
            **Required Format:**
            `Last name, First name - [Document Type]`
            
            **Copy/Paste Templates:**
            * `Smith, John - Research Proposal`
            * `McCall, Debbie - Survey - Interview Questions`
            * `Wolfe-Miller, LaDonna - Parent Permission Form`
            * `Jones, Tommy - Principal-District Permission Forms`
            """)
        else:
            st.markdown("""
            **For External Review:**
            Please include your Name, Institution, and Year:
            
            * `Lastname_Institution_Proposal_2025.pdf`
            * `Lastname_Institution_Instruments_2025.pdf`
            """)
            
    # 4. E-SIGNATURE STANDARDS
    with st.expander("✍️ E-Signature Legal Standards"):
        st.markdown("""
        **📋 Legal Summary: E-Signatures for Student Surveys**
        Electronic signatures are legally valid for parental consent if they meet specific standards (ESIGN Act, FERPA, COPPA).
        
        **⚖️ 1. Governing Legal Frameworks**
        * **ESIGN Act (2000):** Electronic signatures equal "wet-ink" signatures.
        * **FERPA (34 CFR § 99.30):** Allows e-consent if the system **authenticates** the person.
        * **COPPA:** Requires "verifiable parental consent" for kids under 13.
        * **PPRA:** Requires "active" written consent for sensitive topics.

        **🛠️ 2. Core Requirements for Validity**
        To be legally defensible, your e-form must have:
        1.  **Authentication:** Prove the signer is the parent (e.g., "Link sent to verified parent email," "Student ID Check").
        2.  **Intent:** A deliberate action (Checkbox: "By checking this, I provide legal signature").
        3.  **Integrity:** The form cannot be editable after signing.
        4.  **Retention:** Parent must get a copy; School keeps an audit trail (Timestamp + IP).
        """)
    
    st.markdown("---")
    
    # 5. KEY MANAGEMENT (SAFE LOAD)
    district_keys = []
    try:
        if "DISTRICT_KEYS" in st.secrets:
            keys_raw = st.secrets["DISTRICT_KEYS"]
            if isinstance(keys_raw, list):
                district_keys = keys_raw
            elif isinstance(keys_raw, str):
                district_keys = [k.strip() for k in keys_raw.split(",")]
            # Randomize to prevent hotspots
            random.shuffle(district_keys)
            
            if user_mode == "AP Research Student":
                st.success(f"✅ District License Pool Active ({len(district_keys)} Keys)")
                with st.expander("🚀 Performance Boost (Use Your Own Key)"):
                    st.info("Classroom blocked? Use your own free key to bypass the wait.")
                    st.link_button("1. Get Free API Key ↗️", "https://aistudio.google.com/app/apikey")
                    user_key = st.text_input("Paste your personal key:", type="password")
                    if user_key:
                        district_keys = [user_key]
                        st.success("✅ Using Personal Key")
            else:
                st.success("✅ District License Active")
        elif "GOOGLE_API_KEY" in st.secrets:
            district_keys = [st.secrets["GOOGLE_API_KEY"]]
            st.success("✅ Single Key Mode Active")
    except Exception as e:
        st.error(f"Error loading keys: {e}")
        district_keys = []

    st.markdown("---")
    
    # 6. DIAGNOSTICS
    if user_mode == "AP Research Student":
        try:
            lib_ver = importlib.metadata.version("google-generativeai")
        except:
            lib_ver = "Unknown"
        st.caption(f"⚙️ System Version: {lib_ver}")

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
    
    # --- HEADER WITH CUSTOM LOGO ---
    col_logo, col_text = st.columns([1, 8]) 
    
    with col_logo:
        try:
            st.image("APlogo.png", width=100)
        except:
            st.header("🛡️") 
            
    with col_text:
        st.title("AP Research IRB Self-Check Tool")
    
    # --- WORKFLOW GRAPHIC ---
    with st.expander("🗺️ View Research Workflow Map"):
        st.graphviz_chart("""
        digraph {
            rankdir=TB;
            node [shape=box, style="filled,rounded", fontname="Sans-Serif"];
            node [fillcolor="#e1f5fe" color="#01579b"]; # Student Blue
            
            subgraph cluster_0 {
                label = "Phase 1: Development";
                style=dashed; color=grey;
                Draft [label="📝 Draft Proposal"];
                Inst [label="Create Instruments"];
                Draft -> Inst;
            }
            subgraph cluster_1 {
                label = "Phase 2: AI Compliance Check";
                style=filled; color="#e8f5e9";
                node [fillcolor="#c8e6c9" color="#2e7d32"]; # AI Green
                Upload [label="🚀 Upload to AI Portal"];
                Check [label="⚠️ AI Review"];
                Pass [label="✅ Clean Bill of Health"];
                Fail [label="❌ Revision Needed"];
                Inst -> Upload;
                Upload -> Check;
                Check -> Pass;
                Check -> Fail;
                Fail -> Upload [label="Fix & Re-upload"];
            }
            subgraph cluster_2 {
                label = "Phase 3: District Approval";
                style=filled; color="#fff9c4";
                node [fillcolor="#fff59d" color="#fbc02d"]; # District Yellow
                Submit [label="📧 Submit to Mr. Anderson"];
                Review [label="District Committee Review"];
                Approve [label="📜 Approval Letter"];
                Pass -> Submit;
                Submit -> Review;
                Review -> Approve;
                Review -> Fail [label="Denied"];
            }
            subgraph cluster_3 {
                label = "Phase 4: Implementation";
                style=filled; color="#f3e5f5";
                node [fillcolor="#e1bee7" color="#7b1fa2"]; # School Purple
                Principal [label="📍 Contact Principal"];
                Start [label="📊 Begin Data Collection"];
                Approve -> Principal;
                Principal -> Start [label="Site Permission"];
            }
        }
        """)
    
    st.markdown("**For BCS Students:** Screen your research documents against **Policy 6.4001** and **AP Ethics Standards**.&nbsp; Check the sidebar resource to **confirm file-naming standards** for each of your files.")
    st.info("💡 **Tip:** Upload ALL your documents (Proposal, Surveys, Consents) at once for the best analysis.")

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

    if "Principal/District Permission Forms" in selected_docs:
        st.markdown("### 4. Principal/District Permission Forms")
        file = st.file_uploader("Upload Permission Form (PDF)", type="pdf", key="ap_perm")
        if file: student_inputs["PERMISSION_FORM"] = extract_text(file)

    # --- SYSTEM PROMPT (ANTI-LOOP & NO REWRITE) ---
    system_prompt = """
    ROLE: AP Research IRB Compliance Officer for Blount County Schools.
    
    INSTRUCTION: Review the student proposal for compliance with Policy 6.4001. 
    
    **STRICT CONSTRAINTS:** 1. Do NOT rewrite the student's text.
    2. Do NOT provide examples of 'correct' verbiage or phrases to copy.
    3. You must be DESCRIPTIVE and DIRECTIVE (tell them WHAT is missing, not HOW to write it).
    4. **NO REPETITION:** Do not list the same finding multiple times. Group similar issues into a single bullet point.
    
    **HOW TO GENERATE ACTION STEPS:**
    If a section is missing or non-compliant, you must explain the specific *concept* or *data point* that is missing.
    * *Bad:* "Add a data destruction plan."
    * *Good:* "The proposal mentions collecting surveys but fails to specify **when** (date) and **how** (shredding/deletion) the data will be destroyed. Policy 6.4001 requires an explicit timeline for data disposal."
    * *E-Sign Example:* "The proposal uses a Google Form for parent consent but lacks an **Authentication Method**. To be FERPA compliant, you must describe how you will verify the signer is actually the parent (e.g., email verification, student ID check)."
    
    CRITERIA (Policy 6.4001 & Federal Rules):
    1. PROHIBITED: Political affiliation, voting history, religious practices, firearm ownership. (Strict Fail).
    2. SENSITIVE: Mental health, sexual behavior, illegal acts, income. Requires 'Active Written Consent'.
    3. MINOR PROTECTION: Participation is VOLUNTARY. No coercion.
    4. DATA: Must have destruction date and method.
    5. E-SIGNATURES (If applicable): If using electronic consent, check for:
       - **Authentication:** How is the signer identity verified?
       - **Intent:** Is there a clear "I agree" action?
       - **Integrity:** Is the record tamper-proof?
    
    OUTPUT FORMAT:
    - STATUS: [✅ PASS] or [❌ REVISION NEEDED]
    - FINDINGS: Bullet points of observed status.
    - ACTION: Provide detailed instructions on what information must be added to satisfy the policy. Reference specific missing variables (e.g., dates, locations, names, methods).
    """

# ==========================================
# MODE B: EXTERNAL / HIGHER ED RESEARCHER
# ==========================================
else:
    st.title("🏛️ External Research Proposal Review")
    st.info("### 📋 Criteria for External Proposals")
    
    st.markdown("All research requests involving Blount County Schools (BCS) are critiqued against District Standards (Policy 6.4001).&nbsp; Check the sidebar resource to **confirm file-naming standards** for each of your files.")
    
    st.info("You may upload multiple PDF files for each section.")

    external_inputs = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Main Proposal Packet")
        st.caption("Purpose, Methodology, Benefit, Logistics.")
        prop_files = st.file_uploader("Upload Full Proposal (PDFs)", type="pdf", key="ext_prop", accept_multiple_files=True)
        if prop_files:
            combined_text = ""
            for f in prop_files:
                combined_text += extract_text(f) + "\n\n"
            external_inputs["FULL_PROPOSAL"] = combined_text

    with col2:
        st.markdown("### 2. Instruments & Consents")
        st.caption("Surveys, Protocols, Consent Forms.")
        inst_files = st.file_uploader("Upload Instruments (PDFs)", type="pdf", key="ext_inst", accept_multiple_files=True)
        if inst_files:
            combined_text = ""
            for f in inst_files:
                combined_text += extract_text(f) + "\n\n"
            external_inputs["INSTRUMENTS"] = combined_text

    system_prompt = """
    ROLE: Research Committee Reviewer for Blount County Schools (BCS).
    TASK: Analyze the external research proposal against District "Regulations and Procedures for Conducting Research Studies" and Board Policy 6.4001.

    **STRICT CONSTRAINTS:**
    1. Do not provide specific rewrite examples or sample verbiage. 
    2. Provide a professional description of the policy violation or missing element only.
    3. **NO REPETITION:** Do not list the same finding multiple times.

    **GUIDANCE FOR FEEDBACK:**
    Your "Action Items" must be specific enough to guide the researcher without drafting the text for them.
    * *Example:* If the benefit is vague, state: "The proposal lists general academic benefits but lacks a specific, quantifiable benefit to Blount County Schools as required by the district research rubric."

    CRITICAL COMPLIANCE CHECKS:
    1. BENEFIT TO DISTRICT: Must explicitly state "projected value of the study to Blount County."
    2. BURDEN: Must not interfere with instructional time. No "Convenience Sampling."
    3. PROHIBITED TOPICS (Strict Ban): Political affiliation, Voting, Religion, Firearms.
    4. SENSITIVE TOPICS: Mental health, sex, illegal acts, income -> Requires Written Active Consent.
    5. MANDATORY STATEMENTS: Agreement to Policy 6.4001, Voluntary statement, Right to inspect, Anonymity.
    6. E-SIGNATURES (If applicable): Must demonstrate compliance with ESIGN Act/FERPA:
       - **Authentication:** Proof of signer identity.
       - **Audit Trail:** Timestamp and IP tracking.
       - **Retention:** Method for parents to keep a copy.

    OUTPUT FORMAT:
    ### 🚦 Executive Summary
    **Status:** [✅ RECOMMEND FOR REVIEW] or [❌ REVISION NEEDED]
    
    ### 🔍 Compliance Checklist
    (List the 5-6 critical checks above and their status)
    
    ### 📝 Detailed Findings & Action Items
    (Provide specific feedback on *missing variables* or *policy gaps* without offering rewrite text.)
    """
    
    student_inputs = external_inputs

# ==========================================
# EXECUTION LOGIC (ANTI-LOOP & GENTLE ROTATION)
# ==========================================
if st.button("Run Compliance Check"):
    if not district_keys:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not student_inputs:
        st.warning("Please upload at least one document.")
    else:
        # 1. SETUP
        status = st.empty() 
        status.info("🔌 Connecting to AI Services...")
        
        # KEY FIX: Temp 0.5 prevents loops; Top_K 40 keeps it focused.
        generation_config = {
            "temperature": 0.5, 
            "top_p": 0.95, 
            "top_k": 40, 
            "max_output_tokens": 8192
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category":
