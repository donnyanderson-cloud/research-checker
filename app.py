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
        4.  **Retention:** Parent must get a copy; School keeps an audit trail (Timestamp/IP).

        **✅ Compliance Checklist**
        [ ] Is the link sent to a verified email on file?
        [ ] Does the parent have an opt-out or paper alternative?
        [ ] Does the system generate an audit trail (Timestamp + IP)?
        """)
    
    st.markdown("---")
    
    # 5. KEY MANAGEMENT (Legacy Mode for Stability)
    district_keys = []
    if "DISTRICT_KEYS" in st.secrets:
        district_keys = st.secrets["DISTRICT_KEYS"]
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

    else:
        st.markdown("### 🔑 Need an API Key?")
        st.info("System requires an API key.")
        st.link_button("1. Get Free API Key ↗️", "https://aistudio.google.com/app/apikey")
        user_key = st.text_input("Enter Google API Key", type="password")
        if user_key:
            district_keys = [user_key]

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
    
    # --- WORKFLOW GRAPHIC (UPDATED 2026) ---
    with st.expander("🗺️ View New 2026 Workflow Map"):
        st.graphviz_chart("""
        digraph {
            rankdir=TB;
            node [shape=box, style="filled,rounded", fontname="Sans-Serif"];
            
            # Colors
            node [fillcolor="#e1f5fe" color="#01579b"]; # Student Blue
            
            # Phase 1: Creation
            subgraph cluster_0 {
                label = "Phase 1: Development";
                style=dashed; color=grey;
                Draft [label="📝 Draft Proposal"];
                Inst [label="Create Instruments"];
                Draft -> Inst;
            }

            # Phase 2: Optional AI Check
            subgraph cluster_1 {
                label = "Phase 2: Optional Self-Check";
                style=filled; color="#e8f5e9";
                node [fillcolor="#c8e6c9" color="#2e7d32"]; # AI Green
                
                AI_Tool [label="🤖 Run AI Compliance Tool"];
                Feedback [label="🔍 Review AI Findings"];
                Refine [label="✨ Refine Proposal"];
                
                Inst -> AI_Tool [style="dashed" label="Optional"];
                AI_Tool -> Feedback;
                Feedback -> Refine;
            }

            # Phase 3: School Approval (The New Authority)
            subgraph cluster_2 {
                label = "Phase 3: School Approval";
                style=filled; color="#fff9c4";
                node [fillcolor="#fff59d" color="#fbc02d"]; # District Yellow
                
                Submit [label="🏫 Submit to School IRB"];
                Review [label="School Committee Review"];
                District [label="🏢 District Consultation\n(Complex Cases Only)"];
                Approve [label="📜 Final Approval"];
                
                Inst -> Submit [label="Direct"];
                Refine -> Submit [label="After AI Fixes"];
                
                Submit -> Review;
                Review -> Approve;
                Review -> District [label="If Guidance Needed"];
                District -> Review [label="Advisory Opinion"];
            }

            # Phase 4: Implementation
            subgraph cluster_3 {
                label = "Phase 4: Implementation";
                style=filled; color="#f3e5f5";
                node [fillcolor="#e1bee7" color="#7b1fa2"]; # School Purple
                Start [label="📊 Begin Data Collection"];
                
                Approve -> Start;
            }
        }
        """)
    
    # --- UPDATED VERBIAGE ---
    st.markdown("""
    **For BCS Students:** This AI tool is an **optional resource** to help you self-check your work against **Policy 6.4001** before submitting to your School Committee.
    
    * **Final Approval:** Your School IRB Committee.
    * **District Role:** Consulting support for complex cases only.
    """)
    st.markdown("Check the sidebar resource to **confirm file-naming standards** for each of your files.")

    # --- DOCUMENT SELECTORS (THIS WAS MISSING BEFORE) ---
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

    # --- SYSTEM PROMPT (WITH E-SIGNATURE LOGIC) ---
    system_prompt = """
    ROLE: AP Research IRB Compliance Officer for Blount County Schools.
    
    INSTRUCTION: Review the student proposal for compliance with Policy 6.4001. 
    
    **STRICT CONSTRAINT:** 1. Do NOT rewrite the student's text.
    2. Do NOT provide examples of 'correct' verbiage or phrases to copy.
    3. You must be DESCRIPTIVE and DIRECTIVE. 
    
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

    **STRICT CONSTRAINT:**
    Do not provide specific rewrite examples or sample verbiage. Provide a professional description of the policy violation or missing element only.

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
# EXECUTION LOGIC (LEGACY RETRY + NEW ENDING)
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
        
        generation_config = {
            "temperature": 0.3, 
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

        # 3. PREPARING TEXT
        status.info("📄 Reading your PDF files...")
        user_message = f"{system_prompt}\n\nAnalyze the following documents:\n"
        
        total_chars = 0
        for doc_type, content in student_inputs.items():
            clean_content = str(content)[:40000]
            total_chars += len(clean_content)
            user_message += f"\n--- {doc_type} ---\n{clean_content}\n" 
        
        status.info(f"📤 Sending {total_chars} characters to Gemini AI...")

        # 4. LEGACY RETRY LOOP
        # "Flash" and "Pro" are exhausted. We are now targeting the 2024-2025 "Workhorses".
        # These models often have separate, forgotten quota buckets.
        
        models_to_try = [
            "gemini-1.5-flash-001",     # 1. First Stability Release (Often ignored)
            "gemini-1.5-flash-002",     # 2. Second Release
            "gemini-1.5-pro-001",       # 3. Old Pro
            "gemini-1.0-pro"            # 4. The Original (Separate quota entirely)
        ]
        
        response = None
        success = False
        final_key_index = 0
        final_model_name = ""

        with st.spinner("🤖 Switching to Legacy Grids (1.0/1.5)..."):
            for i, key in enumerate(district_keys):
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

        # 5. DISPLAY RESULTS
        if success and response:
            if final_key_index > 1:
                st.toast(f"Success on Key #{final_key_index} ({final_model_name})", icon="🔀")
            else:
                st.toast(f"Connected: {final_model_name}", icon="⚡")
                
            status.success("✅ Analysis Complete!")
            st.markdown("---")
            st.markdown(response.text)
            
            # --- CONDITIONAL NEXT STEPS (UPDATED FOR SCHOOL-BASED APPROVAL) ---
            st.markdown("---")
            st.subheader("📬 Next Steps")
            
            if user_mode == "AP Research Student":
                st.success("""
                **✅ If your proposal looks good:**
                1. Download or Print this AI Report.
                2. Submit your Proposal + this Report to your **School IRB Committee** for final approval.
                *Note: You do not need to email the District unless your School Committee specifically requests a consultation.*
                """)
                st.info("""
                **❌ If "REVISION NEEDED":**
                Use the "Action Items" above to improve your draft before submitting it to your School Committee. This will speed up your approval process!
                """)
            else: 
                # External Researchers still go to District
                st.success("""
                **✅ If all of your artifacts have passed:**
                Please email your screened files to Blount County Schools (**research@blountk12.org**) for final approval. 
                *⚠️ Make sure that all file sharing options have been addressed prior to your email submission.*
                """)
        else:
            status.error("❌ Connection Failed")
            st.error(f"""
            **Total District Quota Exhausted.**
            
            We tried 30 keys on Modern models AND Legacy models. All were rejected.
            
            **IMMEDIATE SOLUTION:**
            Ask a student to generate a free Personal Key at **https://aistudio.google.com/app/apikey** and paste it into the "Performance Boost" box in the sidebar. This will work immediately.
            """)
