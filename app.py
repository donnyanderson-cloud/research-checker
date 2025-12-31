import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import importlib.metadata
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BCS Research Review Portal", page_icon="🏫", layout="wide")

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

    # 2. FILE NAMING GUIDE
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
    
    st.markdown("---")
    
    # 3. INTELLIGENT KEY LOAD BALANCER
    api_key = None
    
    # Check for the list of keys (Primary Method for Classrooms)
    if "DISTRICT_KEYS" in st.secrets:
        key_pool = st.secrets["DISTRICT_KEYS"]
        # Randomly select one key from the pool
        district_key = random.choice(key_pool)
        api_key = district_key
        
        if user_mode == "AP Research Student":
            st.success(f"✅ District License Active")
            with st.expander("🚀 Performance Boost (Use Your Own Key)"):
                st.info("Classroom blocked? Use your own free key to bypass the wait.")
                st.link_button("1. Get Free API Key ↗️", "https://aistudio.google.com/app/apikey")
                user_key = st.text_input("Paste your personal key:", type="password")
                if user_key:
                    api_key = user_key
                    st.success("✅ Using Personal Key")
        else:
            st.success("✅ District License Active")

    # Fallback for Single Key (Legacy Method)
    elif "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        if user_mode == "AP Research Student":
            st.success("✅ District License Active")
            with st.expander("🚀 Performance Boost (Use Your Own Key)"):
                st.info("Classroom blocked? Use your own free key.")
                st.link_button("1. Get Free API Key ↗️", "https://aistudio.google.com/app/apikey")
                user_key = st.text_input("Paste your personal key:", type="password")
                if user_key:
                    api_key = user_key
                    st.success("✅ Using Personal Key")
        else:
            st.success("✅ District License Active")

    else:
        st.markdown("### 🔑 Need an API Key?")
        st.info("System requires an API key.")
        st.link_button("1. Get Free API Key ↗️", "https://aistudio.google.com/app/apikey")
        api_key = st.text_input("Enter Google API Key", type="password")

    st.markdown("---")
    
    # 4. DIAGNOSTICS
    if user_mode == "AP Research Student":
        try:
            lib_ver = importlib.metadata.version("google-generativeai")
        except:
            lib_ver = "Unknown"
        st.caption(f"⚙️ System Version: {lib_ver}")
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
    st.markdown("**For BCS Students:** Screen your research documents against **Policy 6.4001** and **AP Ethics Standards**.")

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

    system_prompt = """
    ROLE: AP Research IRB Compliance Officer for Blount County Schools.
    CRITERIA (Policy 6.4001 & Federal Rules):
    1. PROHIBITED: Political affiliation, voting history, religious practices, firearm ownership. (Strict Fail).
    2. SENSITIVE: Mental health, sexual behavior, illegal acts, income. Requires 'Active Written Consent'.
    3. MINOR PROTECTION: Participation is VOLUNTARY. No coercion.
    4. DATA: Must have destruction date and method.
    OUTPUT: STATUS (PASS/REVISION), FINDINGS, ACTION.
    """

# ==========================================
# MODE B: EXTERNAL / HIGHER ED RESEARCHER
# ==========================================
else:
    st.title("🏛️ External Research Proposal Review")
    st.info("### 📋 Criteria for External Proposals")
    st.markdown("All research requests involving Blount County Schools (BCS) are critiqued against District Standards (Policy 6.4001).")
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

    CRITICAL COMPLIANCE CHECKS:
    1. BENEFIT TO DISTRICT: Must explicitly state "projected value of the study to Blount County."
    2. BURDEN: Must not interfere with instructional time. No "Convenience Sampling."
    3. PROHIBITED TOPICS (Strict Ban): Political affiliation, Voting, Religion, Firearms.
    4. SENSITIVE TOPICS: Mental health, sex, illegal acts, income -> Requires Written Active Consent.
    5. MANDATORY STATEMENTS: Agreement to Policy 6.4001, Voluntary statement, Right to inspect, Anonymity.

    OUTPUT FORMAT:
    ### 🚦 Executive Summary
    **Status:** [RECOMMEND FOR REVIEW] or [REVISION REQUIRED]
    ### 🔍 Compliance Checklist
    ### 📝 Detailed Findings & Action Items
    """
    
    student_inputs = external_inputs

# ==========================================
# EXECUTION LOGIC
# ==========================================
if st.button("Run Compliance Check"):
    if not api_key:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not student_inputs:
        st.warning("Please upload at least one document.")
    else:
        # 1. SETUP
        status = st.empty() 
        status.info("🔌 Connecting to AI Services...")
        genai.configure(api_key=api_key)
        
        # 2. MODEL CONFIG
        generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1, "max_output_tokens": 4096}
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

        # Consolidated Model Definition to prevent Syntax Errors
        model = genai.GenerativeModel(model_name='gemini-flash-latest', generation_config=generation_config, safety_settings=safety_settings)

        # 3. PREPARING TEXT
        status.info("📄 Reading your PDF files...")
        user_message = f"{system_prompt}\n\nAnalyze the following documents:\n"
        
        total_chars = 0
        for doc_type, content in student_inputs.items():
            clean_content = str(content)[:40000]
            total_chars += len(clean_content)
            user_message += f"\n--- {doc_type} ---\n{clean_content}\n" 
        
        status.info(f"📤 Sending {total_chars} characters to Gemini AI...")

        # 4. SENDING REQUEST
        with st.spinner("🤖 Analyzing against District Policy..."):
            try:
                response = model.generate_content(user_message)
                status.success("✅ Analysis Complete!")
                st.markdown("---")
                
                # DISPLAY THE AI ANALYSIS
                st.markdown(response.text)
                
                # --- CONDITIONAL NEXT STEPS ---
                st.markdown("---")
                st.subheader("📬 Next Steps")
                
                if user_mode == "AP Research Student":
                    st.info("""
                    **If all of your artifacts have passed:**
                    1. Confirm your status to your teacher for district submission via email: **donny.anderson@blountk12.org**
                    2. Make sure that all files that were AI screened are shared with Mr. Anderson.
                    
                    **If your Status is ❌ REVISION NEEDED:**
                    * Review the "Action Items" above, edit your documents, and re-run this check.
                    """)
                    
                else: # External Researcher
                    st.success("""
                    **✅ If all of your artifacts have passed:**
                    Please email your screened files to Blount County Schools (**research@blountk12.org**) for final approval. 
                    *⚠️ Make sure that all file sharing options have been addressed prior to your email submission (ensure links are public/viewable).*
                    """)
                    
                    st.warning("""
                    **❌ If the Analysis says "REVISION REQUIRED":**
                    Please correct the items listed in the checklist above before emailing the district. 
                    Non-compliant proposals will be automatically returned.
                    """)
                
            except Exception as e:
                status.error("❌ Analysis Failed")
                st.error(f"Error details: {e}")
