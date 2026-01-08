import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import importlib.metadata
import random
import time
import re
from datetime import datetime

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
    
    # 5. KEY MANAGEMENT (SAFE LOAD + SHUFFLE)
    district_keys = []
    try:
        if "DISTRICT_KEYS" in st.secrets:
            keys_raw = st.secrets["DISTRICT_KEYS"]
            if isinstance(keys_raw, list):
                district_keys = keys_raw
            elif isinstance(keys_raw, str):
                district_keys = [k.strip() for k in keys_raw.split(",")]
            
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
    
    # 6. DIAGNOSTICS & UPDATES
    if user_mode == "AP Research Student":
        try:
            lib_ver = importlib.metadata.version("google-generativeai")
        except:
            lib_ver = "Unknown"
        st.caption(f"⚙️ System Version: {lib_ver}")
        
        with st.expander("Recent Updates"):
            st.caption("""
            **v2.3 - Patched Jan 8, 2026**
            1. **PDF Report:** Now generates official PDF findings (emojis stripped).
            2. **Workflow:** Terminology updated to "School Review Committee".
            3. **Logic:** District Forms now "Advisory" (Not Auto-Fail).
            4. **Tracker:** Added Live API Key Usage notification.
            5. **Fix:** Solved "Repetitive Loop" bug (Temp 0.5).
            """)

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

# --- HELPER FUNCTION: PDF REPORT GENERATION ---
def create_pdf_report(student_name, ai_text):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'OFFICIAL RESEARCH COMPLIANCE REPORT', 0, 1, 'C')
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, 'Blount County Schools - IRB Screening Tool', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    # Remove Emojis (Simple Regex to keep basic text/punctuation)
    # This prevents latin-1 encoding errors common in FPDF
    clean_text = re.sub(r'[^\x00-\x7F]+', '', ai_text)
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Meta Data
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    pdf.cell(40, 10, f"Student Name: {student_name}", 0, 1)
    pdf.ln(5)
    
    # Body
    pdf.set_font("Arial", size=11)
    # MultiCell is used for text wrapping
    pdf.multi_cell(0, 7, clean_text)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# MODE A: AP RESEARCH STUDENT
# ==========================================
if user_mode == "AP Research Student":
    
    col_logo, col_text = st.columns([1, 8]) 
    with col_logo:
        try:
            st.image("APlogo.png", width=100)
        except:
            st.header("🛡️") 
            
    with col_text:
        st.title("AP Research IRB Self-Check Tool")
    
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
                label = "Phase 3: School Level Approval";
                style=filled; color="#fff9c4";
                node [fillcolor="#fff59d" color="#fbc02d"]; # District Yellow
                Teacher [label="👩‍🏫 Confirm w/ Teacher"];
                Committee [label="🏫 School Review Committee"];
                
                Pass -> Teacher;
                Teacher -> Committee;
                Committee -> Fail [label="Revisions"];
            }
            subgraph cluster_3 {
                label = "Phase 4: Implementation";
                style=filled; color="#f3e5f5";
                node [fillcolor="#e1bee7" color="#7b1fa2"]; # School Purple
                Principal [label="📍 Contact Principal"];
                Start [label="📊 Begin Data Collection"];
                Committee -> Principal [label="Approved"];
                Principal -> Start [label="Site Permission"];
            }
        }
        """)
    
    st.markdown("**For BCS Students:** Screen your research documents against **Policy 6.4001** and **AP Ethics Standards**.")
    st.info("💡 **Tip:** Upload ALL your documents (Proposal, Surveys, Consents) at once for the best analysis.")

    # --- STUDENT NAME INPUT (FOR REPORT) ---
    st.markdown("### 1. Student Details")
    student_name = st.text_input("Enter Student Name (for Official Report):", placeholder="Last Name, First Name")

    st.markdown("### 2. Upload Documents")
    document_types = [
        "Research Proposal",
        "Survey / Interview Questions",
        "Parent Permission Form",
        "Principal Permission Form (District Form if applicable)" 
    ]
    selected_docs = st.multiselect("Select documents to screen:", document_types, default=["Research Proposal"])
    
    student_inputs = {}

    if "Research Proposal" in selected_docs:
        file = st.file_uploader("Upload Proposal (PDF)", type="pdf", key="ap_prop")
        if file: student_inputs["PROPOSAL"] = extract_text(file)

    if "Survey / Interview Questions" in selected_docs:
        input_method = st.radio("Input Method:", ["Paste Text", "Upload PDF"], horizontal=True, key="ap_survey_toggle")
        if input_method == "Paste Text":
            st.info("💡 Tip: For Google Forms, Ctrl+A -> Copy -> Paste here.")
            text = st.text_area("Paste text here:", height=200, key="ap_survey_text")
            if text: student_inputs["SURVEY"] = text
        else:
            file = st.file_uploader("Upload Survey PDF", type="pdf", key="ap_survey_file")
            if file: student_inputs["SURVEY"] = extract_text(file)

    if "Parent Permission Form" in selected_docs:
        file = st.file_uploader("Upload Parent Form (PDF)", type="pdf", key="ap_parent")
        if file: student_inputs["PARENT_FORM"] = extract_text(file)

    if "Principal Permission Form (District Form if applicable)" in selected_docs:
        file = st.file_uploader("Upload Signed Permission Form (PDF)", type="pdf", key="ap_perm")
        if file: student_inputs["PERMISSION_FORM"] = extract_text(file)

    # --- SYSTEM PROMPT ---
    system_prompt = """
    ROLE: AP Research IRB Compliance Officer for Blount County Schools.
    
    INSTRUCTION: Review the student proposal for compliance with Policy 6.4001. 
    
    **CONTEXTUAL INTELLIGENCE (METHODOLOGY CHECK):** 1. First, determine the study's methodology.
    2. **IF** the study is Observational, Archival, or Content Analysis (no interaction with human subjects), DO NOT flag missing permissions, consent forms, or survey instruments.
    3. **IF** the study involves Surveys, Interviews, or Focus Groups (Human Subjects), YOU MUST enforce all consent and permission requirements strictly.
    4. **PERMISSION CHECK (ADVISORY):** All school-based research requires **Principal Permission**. If the proposal involves multiple schools or district-wide data and the District Form is missing, **DO NOT FAIL**. Instead, mark it as a "Recommendation" for the AP Teacher/School Review Committee to review.
    
    **STRICT CONSTRAINTS:** 1. Do NOT rewrite the student's text.
    2. Do NOT provide examples of 'correct' verbiage or phrases to copy.
    3. You must be DESCRIPTIVE and DIRECTIVE (tell them WHAT is missing, not HOW to write it).
    4. **NO REPETITION:** Do not list the same finding multiple times.
    
    **HOW TO GENERATE ACTION STEPS:**
    If a section is missing or non-compliant, you must explain the specific *concept* or *data point* that is missing.
    * *Permission Example:* "The proposal involves multiple schools. **Action:** Please consult your AP Research Teacher or **School Review Committee** to determine if a formal District Permission Form is required for this scope."
    
    CRITERIA (Policy 6.4001 & Federal Rules):
    1. PROHIBITED: Political affiliation, voting history, religious practices, firearm ownership. (Strict Fail).
    2. SENSITIVE: Mental health, sexual behavior, illegal acts, income. Requires 'Active Written Consent'.
    3. MINOR PROTECTION: Participation is VOLUNTARY. No coercion.
    4. DATA: Must have destruction date and method.
    5. E-SIGNATURES (Conditional): **IF** using electronic consent, check for Authentication, Intent, and Integrity.
    
    OUTPUT FORMAT:
    - STATUS: [PASS] or [REVISION NEEDED] or [TEACHER REVIEW RECOMMENDED] (Do not use emojis).
    - FINDINGS: Bullet points of observed status.
    - ACTION: Detailed instructions.
    """

# ==========================================
# MODE B: EXTERNAL / HIGHER ED RESEARCHER
# ==========================================
else:
    st.title("🏛️ External Research Proposal Review")
    st.info("### 📋 Criteria for External Proposals")
    
    st.markdown("All research requests involving Blount County Schools (BCS) are critiqued against District Standards (Policy 6.4001).")
    external_inputs = {}
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Main Proposal Packet")
        prop_files = st.file_uploader("Upload Full Proposal (PDFs)", type="pdf", key="ext_prop", accept_multiple_files=True)
        if prop_files:
            combined_text = ""
            for f in prop_files:
                combined_text += extract_text(f) + "\n\n"
            external_inputs["FULL_PROPOSAL"] = combined_text

    with col2:
        st.markdown("### 2. Instruments & Consents")
        inst_files = st.file_uploader("Upload Instruments (PDFs)", type="pdf", key="ext_inst", accept_multiple_files=True)
        if inst_files:
            combined_text = ""
            for f in inst_files:
                combined_text += extract_text(f) + "\n\n"
            external_inputs["INSTRUMENTS"] = combined_text

    system_prompt = """
    ROLE: Research Committee Reviewer for Blount County Schools (BCS).
    TASK: Analyze the external research proposal against District "Regulations and Procedures for Conducting Research Studies" and Board Policy 6.4001.
    (See internal constraints for details).
    """
    
    student_inputs = external_inputs

# ==========================================
# EXECUTION LOGIC
# ==========================================
if st.button("Run Compliance Check"):
    if not district_keys:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not student_inputs:
        st.warning("Please upload at least one document.")
    else:
        status = st.empty() 
        status.info("🔌 Connecting to AI Services...")
        
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
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

        # PREPARING TEXT
        status.info("📄 Reading your PDF files...")
        user_message = f"{system_prompt}\n\nAnalyze the following documents:\n"
        
        for doc_type, content in student_inputs.items():
            clean_content = str(content)[:40000]
            user_message += f"\n--- {doc_type} ---\n{clean_content}\n" 
        
        status.info(f"📤 Sending data to Gemini AI...")

        # GENTLE KEY ROTATION
        models_to_try = [
            "gemini-1.5-flash-8b", 
            "gemini-2.5-flash-lite", 
            "gemini-1.5-flash"
        ]
        
        response = None
        success = False
        final_key_index = 0
        final_model_name = ""

        with st.spinner(f"🤖 Cycling through {len(district_keys)} keys (Gentle Mode)..."):
            for i, key in enumerate(district_keys):
                if i > 0: time.sleep(0.5)
                genai.configure(api_key=key)
                
                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(
                            model_name=model_name, 
                            generation_config=generation_config, 
                            safety_settings=safety_settings
                        )
                        response = model.generate_content(user_message)
                        success = True
                        final_key_index = i + 1
                        final_model_name = model_name
                        break 
                    except Exception:
                        continue
                if success:
                    break

        # DISPLAY RESULTS
        if success and response:
            if final_key_index > 1:
                st.toast(f"⚠️ Load Balanced: Key #{final_key_index}", icon="🔀")
            else:
                st.toast(f"⚡ Connected using Key #{final_key_index}", icon="⚡")
                
            status.success("✅ Analysis Complete!")
            
            # --- PDF REPORT GENERATION (NEW FEATURE) ---
            try:
                pdf_bytes = create_pdf_report(
                    student_name if student_name else "Student", 
                    response.text
                )
                
                st.download_button(
                    label="📄 Download Official PDF Report",
                    data=pdf_bytes,
                    file_name=f"IRB_Findings_{student_name.replace(' ', '_') if student_name else 'Report'}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
            # ---------------------------------------

            st.markdown("---")
            st.markdown(response.text)
            
            st.markdown("---")
            st.subheader("📬 Next Steps")
            
            if user_mode == "AP Research Student":
                st.success("""
                **✅ If all of your artifacts have passed:**
                1. **Confirm your status with your AP Research Teacher.**
                2. Plan for your **School Review Committee** meeting.
                3. Ensure all screened files are organized and ready for final review.
                """)
                st.error("""
                **❌ If your Status is REVISION NEEDED:**
                * Review the "Action Items" above.
                * Edit your documents to address the missing policy requirements.
                * **Re-run this check** until you get a PASS status.
                """)
            else: 
                st.success("""
                **✅ If all of your artifacts have passed:**
                Please email your screened files to Blount County Schools (**research@blountk12.org**) for final approval. 
                """)
                st.error("""
                **❌ If the Analysis says "REVISION NEEDED":**
                Please correct the items listed in the checklist above before emailing the district. 
                """)
        else:
            status.error("❌ Connection Failed")
            st.error(f"System Exhausted: We tried {len(district_keys)} keys and all were rejected.")
