import streamlit as st
import time

# Import your new modularized logic
from core.analysis import analyze_resume
from utils.file_parsing import parse_pdf, parse_docx

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    .stMetric label { color: rgba(255, 255, 255, 0.9) !important; }
    .stMetric .metric-value { color: white !important; }

    .big-score {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .score-value {
        font-size: 4rem;
        font-weight: bold;
        color: white;
    }
    .score-label {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
    }

    .keyword-found {
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        display: inline-block;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .keyword-missing {
        background-color: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        display: inline-block;
        margin: 0.25rem;
        font-size: 0.9rem;
    }

    .suggestion-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
        color: #1f2937;
    }
    .suggestion-warning {
        background-color: #fef3c7;
        border-left-color: #f59e0b;
        color: #78350f;
    }
    .suggestion-danger {
        background-color: #fee2e2;
        border-left-color: #ef4444;
        color: #7f1d1d;
    }
    .suggestion-info {
        background-color: #dbeafe;
        border-left-color: #3b82f6;
        color: #1e3a8a;
    }
    .suggestion-success {
        background-color: #d1fae5;
        border-left-color: #10b981;
        color: #064e3b;
    }
    .suggestion-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("📄 Resume Optimizer")
st.markdown("### AI-powered resume analysis and optimization")

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# ---------------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------------
with st.sidebar:
    st.header("Input Your Information")

    # Upload resume
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "pdf", "docx"],
        help="Upload your resume as PDF, DOCX, or TXT"
    )

    # Paste text
    st.subheader("Or Paste Resume Text")
    resume_text = st.text_area(
        "Resume Text",
        height=300,
        placeholder="Paste your resume text here..."
    )

    # Handle file upload
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            resume_text = uploaded_file.read().decode("utf-8")

        elif uploaded_file.type == "application/pdf":
            resume_text = parse_pdf(uploaded_file)

        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = parse_docx(uploaded_file)

        else:
            st.warning("Unsupported file type. Please upload TXT, PDF, or DOCX.")

    st.divider()

    # Job description
    st.subheader("🎯 Job Description (Optional)")
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here..."
    )

    st.divider()

    # Analyze button
    analyze_button = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# ---------------------------------------------------------
# ANALYSIS LOGIC
# ---------------------------------------------------------
if analyze_button and resume_text:
    with st.spinner("🔍 Analyzing your resume..."):
        time.sleep(1)
        results = analyze_resume(resume_text, job_description)
        st.session_state.analyzed = True
        st.session_state.results = results

elif analyze_button and not resume_text:
    st.error("⚠️ Please provide your resume text")

# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------
if st.session_state.analyzed:
    results = st.session_state.results

    # Overall score
    st.markdown(f"""
    <div class="big-score">
        <div class="score-value">{results['overall_score']}</div>
        <div class="score-label">Overall Score</div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🔑 Keywords",
        "💡 Suggestions",
        "✏️ Specific Changes",
        "✅ ATS Check"
    ])

    # -----------------------------------------------------
    # TAB 1 — OVERVIEW
    # -----------------------------------------------------
    with tab1:
        st.subheader("Performance Metrics")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Keywords Match", f"{results['keyword_score']}%")
        col2.metric("ATS Compatibility", f"{results['ats_score']}%")
        col3.metric("Impact Verbs", f"{results['impact_score']}%")
        col4.metric("Quantifiable Results", f"{results['quant_score']}%")

        st.divider()

        st.subheader("Quick Insights")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Impact Verbs Found:**")
            if results["impact_verbs"]:
                st.write(", ".join(results["impact_verbs"][:10]))
            else:
                st.write("*None found — consider adding action verbs*")

        with col2:
            st.write("**Keyword Match Rate:**")
            if job_description:
                total = len(results["found_keywords"]) + len(results["missing_keywords"])
                if total > 0:
                    st.progress(len(results["found_keywords"]) / total)
                    st.write(f"{len(results['found_keywords'])} of {total} keywords found")
            else:
                st.write("*Add job description for keyword analysis*")

        st.divider()
        st.info("💡 **Pro Tip**: Balance keywords with authentic achievements. Avoid keyword stuffing.")

    # -----------------------------------------------------
    # TAB 2 — KEYWORDS
    # -----------------------------------------------------
    with tab2:
        st.subheader("Keyword Analysis")

        if job_description:
            col1, col2 = st.columns(2)

            with col1:
                st.write("### ✅ Found Keywords")
                if results["found_keywords"]:
                    for kw in results["found_keywords"]:
                        st.markdown(f'<span class="keyword-found">✓ {kw}</span>', unsafe_allow_html=True)
                else:
                    st.info("No keywords found")

            with col2:
                st.write("### ❌ Missing Keywords")
                if results["missing_keywords"]:
                    st.write("*Consider incorporating these naturally:*")
                    for kw in results["missing_keywords"]:
                        st.markdown(f'<span class="keyword-missing">✗ {kw}</span>', unsafe_allow_html=True)
                else:
                    st.success("All keywords found!")

            st.divider()
            st.warning("⚠️ Avoid keyword stuffing. Use keywords naturally.")
        else:
            st.info("📝 Add a job description to see keyword analysis")

    # -----------------------------------------------------
    # TAB 3 — SUGGESTIONS
    # -----------------------------------------------------
    with tab3:
        st.subheader("Optimization Suggestions")

        if results["suggestions"]:
            for suggestion in results["suggestions"]:
                st.markdown(f"""
                <div class="suggestion-box suggestion-{suggestion['type']}">
                    <div class="suggestion-title">{suggestion['title']}</div>
                    <div>{suggestion['description']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✨ Your resume looks great! No major suggestions.")

    # -----------------------------------------------------
    # TAB 4 — SPECIFIC CHANGES
    # -----------------------------------------------------
    with tab4:
        st.subheader("Specific Line-by-Line Changes")

        if results["specific_changes"]:
            st.write("Here are specific improvements you can make:")

            for change in results["specific_changes"]:
                with st.expander(f"📝 Line {change['line_number']}: {change['original'][:60]}..."):
                    st.markdown("**Original:**")
                    st.code(change["original"])
                    st.markdown("**Suggestions:**")
                    for i, suggestion in enumerate(change["suggestions"], 1):
                        st.markdown(f"{i}. {suggestion}")

            st.divider()
            st.info("💡 Only apply changes that reflect your real experience.")
        else:
            st.success("✨ Your bullet points look strong!")

    # -----------------------------------------------------
    # TAB 5 — ATS CHECK
    # -----------------------------------------------------
    with tab5:
        st.subheader("ATS Compatibility Check")

        if results["ats_issues"]:
            for issue in results["ats_issues"]:
                st.markdown(f"""
                <div class="suggestion-box suggestion-{issue['type']}">
                    <div class="suggestion-title">{issue['title']}</div>
                    <div>{issue['description']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="suggestion-box suggestion-success">
                <div class="suggestion-title">✓ ATS Compatible</div>
                <div>Your resume appears well-formatted for ATS.</div>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# WELCOME MESSAGE
# ---------------------------------------------------------
else:
    st.info("""
    ### 👋 Welcome to Resume Optimizer!

    Get started by:
    1. Uploading your resume or pasting the text
    2. (Optional) Adding a job description
    3. Clicking **Analyze Resume**

    The tool will analyze:
    - 📊 Keyword matching  
    - 💪 Impact verbs  
    - 📈 Quantifiable results  
    - ✅ ATS compatibility  
    - 💡 Improvement suggestions  
    """)
