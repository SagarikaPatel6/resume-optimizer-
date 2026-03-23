import streamlit as st
import re
from collections import Counter
import time

# Page configuration
st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    
    .stMetric label {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stMetric .metric-value {
        color: white !important;
    }
    
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
    }
    
    .suggestion-warning {
        background-color: #fef3c7;
        border-left-color: #f59e0b;
    }
    
    .suggestion-danger {
        background-color: #fee2e2;
        border-left-color: #ef4444;
    }
    
    .suggestion-info {
        background-color: #dbeafe;
        border-left-color: #3b82f6;
    }
    
    .suggestion-success {
        background-color: #d1fae5;
        border-left-color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📄 Resume Optimizer")
st.markdown("### AI-powered resume analysis and optimization")

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

# Sidebar for inputs
with st.sidebar:
    st.header("Input Your Information")
    
    # File upload option
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'pdf', 'docx'],
        help="Upload your resume as PDF, DOCX, or TXT"
    )
    
    # Text input option
    st.subheader("Or Paste Resume Text")
    resume_text = st.text_area(
        "Resume Text",
        height=300,
        placeholder="Paste your resume text here..."
    )
    
    # Handle file upload
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            resume_text = uploaded_file.read().decode('utf-8')
        else:
            st.warning("PDF/DOCX parsing requires additional libraries. Please paste text instead or use TXT files.")
    
    st.divider()
    
    # Job description input
    st.subheader("🎯 Job Description (Optional)")
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here for tailored analysis..."
    )
    
    st.divider()
    
    # Analyze button
    analyze_button = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)


def extract_keywords(text, min_length=4):
    """Extract keywords from text"""
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'such', 'which', 'what', 'who', 'when', 'where',
        'why', 'how', 'their', 'there', 'they', 'them', 'then', 'than',
        'your', 'you', 'we', 'our', 'us', 'it', 'its'
    }
    
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if len(w) >= min_length and w not in common_words]
    return list(set(keywords))


def count_impact_verbs(text):
    """Count impact verbs in resume"""
    impact_verbs = [
        'achieved', 'improved', 'increased', 'decreased', 'developed',
        'created', 'led', 'managed', 'launched', 'implemented', 'delivered',
        'designed', 'built', 'optimized', 'streamlined', 'orchestrated',
        'spearheaded', 'pioneered', 'transformed', 'established', 'drove',
        'executed', 'accelerated', 'generated', 'maximized', 'enhanced'
    ]
    
    text_lower = text.lower()
    found_verbs = [verb for verb in impact_verbs if verb in text_lower]
    return len(found_verbs), found_verbs


def count_quantifiable_results(text):
    """Count quantifiable metrics in resume"""
    patterns = [
        r'\d+%',  # percentages
        r'\d+\+',  # numbers with plus
        r'[$€£]\d+',  # money
        r'\d+[xX]',  # multipliers
        r'\d+\s*(million|billion|thousand|k|m|b)',  # large numbers
    ]
    
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text))
    return count


def check_ats_compatibility(text):
    """Check for ATS compatibility issues"""
    issues = []
    
    # Check for tabs
    if '\t' in text:
        issues.append({
            'type': 'warning',
            'title': 'Contains Tabs',
            'description': 'Replace tabs with spaces for better ATS compatibility.'
        })
    
    # Check for special bullets
    if re.search(r'[•●○■□▪▫]', text):
        issues.append({
            'type': 'warning',
            'title': 'Special Bullet Characters',
            'description': 'Use standard bullets (-, *, or •) instead of special Unicode characters.'
        })
    
    # Check for section headers
    text_lower = text.lower()
    if 'experience' not in text_lower and 'work history' not in text_lower:
        issues.append({
            'type': 'danger',
            'title': 'Missing Experience Section',
            'description': 'Add a clear "Experience" or "Work History" section header.'
        })
    
    if 'education' not in text_lower:
        issues.append({
            'type': 'info',
            'title': 'Missing Education Section',
            'description': 'Consider adding an "Education" section if applicable.'
        })
    
    # Check for contact information
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        issues.append({
            'type': 'warning',
            'title': 'No Email Found',
            'description': 'Make sure your email address is clearly visible.'
        })
    
    return issues


def generate_suggestions(resume, job_desc, impact_verb_count, quant_count, keyword_match_rate):
    """Generate improvement suggestions"""
    suggestions = []
    
    # Impact verbs suggestion
    if impact_verb_count < 5:
        suggestions.append({
            'type': 'warning',
            'title': 'Use More Action Verbs',
            'description': 'Start bullet points with strong action verbs like "achieved," "led," "developed," or "implemented" to demonstrate impact.'
        })
    
    # Quantifiable results suggestion
    if quant_count < 3:
        suggestions.append({
            'type': 'danger',
            'title': 'Add Quantifiable Results',
            'description': 'Include specific metrics and numbers (e.g., "Increased sales by 25%" or "Managed team of 10") to demonstrate tangible impact.'
        })
    
    # Keyword match suggestion
    if job_desc and keyword_match_rate < 50:
        suggestions.append({
            'type': 'danger',
            'title': 'Low Keyword Match',
            'description': 'Your resume is missing many keywords from the job description. Incorporate relevant skills and terms naturally throughout your resume.'
        })
    
    # Resume length suggestion
    if len(resume) < 500:
        suggestions.append({
            'type': 'warning',
            'title': 'Resume Seems Short',
            'description': 'Consider expanding your experience descriptions with more detail about your achievements and responsibilities.'
        })
    
    # Professional links suggestion
    resume_lower = resume.lower()
    if 'linkedin' not in resume_lower and 'github' not in resume_lower and 'http' not in resume_lower:
        suggestions.append({
            'type': 'info',
            'title': 'Add Professional Links',
            'description': 'Include your LinkedIn profile, GitHub, or portfolio website to provide recruiters with more context about your work.'
        })
    
    # Skills section suggestion
    if 'skills' not in resume_lower and 'technical skills' not in resume_lower:
        suggestions.append({
            'type': 'info',
            'title': 'Add Skills Section',
            'description': 'Include a dedicated skills section highlighting your technical and professional competencies.'
        })
    
    return suggestions


def analyze_resume(resume, job_desc):
    """Main analysis function"""
    # Extract keywords
    job_keywords = extract_keywords(job_desc) if job_desc else []
    resume_lower = resume.lower()
    
    # Find matching and missing keywords
    found_keywords = [kw for kw in job_keywords if kw in resume_lower]
    missing_keywords = [kw for kw in job_keywords if kw not in resume_lower]
    
    # Calculate keyword score
    if job_keywords:
        keyword_score = (len(found_keywords) / len(job_keywords)) * 100
    else:
        keyword_score = 75  # Default if no job description
    
    # Count impact verbs
    impact_verb_count, impact_verbs = count_impact_verbs(resume)
    impact_score = min(100, (impact_verb_count / 8) * 100)
    
    # Count quantifiable results
    quant_count = count_quantifiable_results(resume)
    quant_score = min(100, (quant_count / 5) * 100)
    
    # Check ATS compatibility
    ats_issues = check_ats_compatibility(resume)
    ats_score = max(0, 100 - (len(ats_issues) * 15))
    
    # Generate suggestions
    suggestions = generate_suggestions(resume, job_desc, impact_verb_count, quant_count, keyword_score)
    
    # Calculate overall score
    overall_score = (keyword_score + ats_score + impact_score + quant_score) / 4
    
    return {
        'overall_score': round(overall_score),
        'keyword_score': round(keyword_score),
        'ats_score': round(ats_score),
        'impact_score': round(impact_score),
        'quant_score': round(quant_score),
        'found_keywords': found_keywords[:20],  # Top 20
        'missing_keywords': missing_keywords[:20],  # Top 20
        'impact_verbs': impact_verbs,
        'suggestions': suggestions,
        'ats_issues': ats_issues
    }


# Main analysis logic
if analyze_button and resume_text:
    with st.spinner('🔍 Analyzing your resume...'):
        time.sleep(1)  # Simulate processing
        results = analyze_resume(resume_text, job_description)
        st.session_state.analyzed = True
        st.session_state.results = results

elif analyze_button and not resume_text:
    st.error("⚠️ Please provide your resume text")

# Display results
if st.session_state.analyzed:
    results = st.session_state.results
    
    # Overall score
    st.markdown(f"""
    <div class="big-score">
        <div class="score-value">{results['overall_score']}</div>
        <div class="score-label">Overall Score</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔑 Keywords", "💡 Suggestions", "✅ ATS Check"])
    
    with tab1:
        st.subheader("Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Keywords Match", f"{results['keyword_score']}%")
        
        with col2:
            st.metric("ATS Compatibility", f"{results['ats_score']}%")
        
        with col3:
            st.metric("Impact Verbs", f"{results['impact_score']:.0f}%")
        
        with col4:
            st.metric("Quantifiable Results", f"{results['quant_score']:.0f}%")
        
        st.divider()
        
        # Additional insights
        st.subheader("Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Impact Verbs Found:**")
            if results['impact_verbs']:
                st.write(", ".join(results['impact_verbs'][:10]))
            else:
                st.write("*None found - consider adding action verbs*")
        
        with col2:
            st.write("**Keyword Match Rate:**")
            if job_description:
                total = len(results['found_keywords']) + len(results['missing_keywords'])
                if total > 0:
                    st.progress(len(results['found_keywords']) / total)
                    st.write(f"{len(results['found_keywords'])} of {total} keywords found")
            else:
                st.write("*Add job description for keyword analysis*")
    
    with tab2:
        st.subheader("Keyword Analysis")
        
        if job_description:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### ✅ Found Keywords")
                if results['found_keywords']:
                    for kw in results['found_keywords']:
                        st.markdown(f'<span class="keyword-found">✓ {kw}</span>', unsafe_allow_html=True)
                else:
                    st.info("No keywords found")
            
            with col2:
                st.write("### ❌ Missing Keywords")
                if results['missing_keywords']:
                    for kw in results['missing_keywords']:
                        st.markdown(f'<span class="keyword-missing">✗ {kw}</span>', unsafe_allow_html=True)
                else:
                    st.success("All keywords found!")
        else:
            st.info("📝 Add a job description to see keyword analysis")
    
    with tab3:
        st.subheader("Optimization Suggestions")
        
        if results['suggestions']:
            for suggestion in results['suggestions']:
                st.markdown(f"""
                <div class="suggestion-box suggestion-{suggestion['type']}">
                    <strong>{suggestion['title']}</strong><br>
                    {suggestion['description']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✨ Your resume looks great! No major suggestions.")
    
    with tab4:
        st.subheader("ATS Compatibility Check")
        
        if results['ats_issues']:
            for issue in results['ats_issues']:
                st.markdown(f"""
                <div class="suggestion-box suggestion-{issue['type']}">
                    <strong>{issue['title']}</strong><br>
                    {issue['description']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="suggestion-box suggestion-success">
                <strong>✓ ATS Compatible</strong><br>
                Your resume appears to be well-formatted for Applicant Tracking Systems.
            </div>
            """, unsafe_allow_html=True)

else:
    # Welcome message when no analysis has been done
    st.info("""
    ### 👋 Welcome to Resume Optimizer!
    
    Get started by:
    1. **Upload** your resume or **paste** the text in the sidebar
    2. (Optional) Add a **job description** for tailored analysis
    3. Click **Analyze Resume** to get instant feedback
    
    Our AI will analyze:
    - 📊 Keyword matching with job descriptions
    - ✅ ATS compatibility
    - 💪 Impact verbs and action words
    - 📈 Quantifiable results and metrics
    - 💡 Personalized improvement suggestions
    """)
