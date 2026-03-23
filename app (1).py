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


def generate_specific_changes(resume, job_desc, missing_keywords, impact_verbs):
    """Generate specific line-by-line change recommendations"""
    changes = []
    resume_lines = resume.split('\n')
    
    # Find bullet points that could be improved
    for i, line in enumerate(resume_lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Check if it's a bullet point
        is_bullet = line_stripped.startswith(('-', '•', '*', '●')) or line_stripped[0].isdigit() and '.' in line_stripped[:3]
        
        if is_bullet:
            # Remove bullet character
            clean_line = re.sub(r'^[\-•*●\d\.]\s*', '', line_stripped)
            
            # Check if starts with action verb
            first_word = clean_line.split()[0].lower() if clean_line.split() else ''
            has_impact_verb = any(verb in clean_line.lower() for verb in impact_verbs)
            
            # Check if has quantifiable results
            has_numbers = bool(re.search(r'\d+%|\d+\+|[$€£]\d+|\d+[xX]|\d+\s*(million|billion|thousand|k|m|b)', clean_line))
            
            suggestions_for_line = []
            
            if not has_impact_verb and len(clean_line) > 10:
                suggestions_for_line.append("Start with an action verb (e.g., 'Developed', 'Led', 'Implemented')")
            
            if not has_numbers and len(clean_line) > 10:
                suggestions_for_line.append("Add quantifiable metrics or results")
            
            # Check for relevant missing keywords that could fit
            relevant_keywords = [kw for kw in missing_keywords[:10] if kw not in clean_line.lower()]
            if relevant_keywords and len(suggestions_for_line) > 0:
                suggestions_for_line.append(f"Consider incorporating: {', '.join(relevant_keywords[:3])}")
            
            if suggestions_for_line:
                changes.append({
                    'line_number': i + 1,
                    'original': line_stripped,
                    'suggestions': suggestions_for_line
                })
    
    return changes[:15]  # Limit to top 15 changes


def generate_optimized_resume(resume, job_desc, found_keywords, missing_keywords):
    """Generate AI-powered optimized resume suggestions"""
    
    prompt = f"""I need help optimizing a resume to better match a job description while keeping it natural and authentic.

**Important Guidelines:**
- Keep the person's actual experience and achievements
- Make changes subtle and organic
- Don't stuff keywords unnaturally
- Focus on impact and clarity
- Maintain professional tone

**Job Description Key Requirements:**
{', '.join(missing_keywords[:15]) if missing_keywords else 'General improvements'}

**Current Resume:**
{resume[:2000]}

Please provide 5-7 specific, actionable improvements focusing on:
1. Better action verbs where appropriate
2. Adding quantifiable results
3. Naturally incorporating missing keywords
4. Improving clarity and impact
5. Making accomplishments more concrete

Format each as: "Change [specific text] to [improved version] because [brief reason]"
"""
    
    # This is a placeholder - in production, you'd call an AI API
    # For now, return structured guidance
    return prompt


def analyze_resume(resume, job_desc):
    """Main analysis function"""
    # Extract keywords
    job_keywords = extract_keywords(job_desc) if job_desc else []
    resume_lower = resume.lower()
    
    # Find matching and missing keywords
    found_keywords = [kw for kw in job_keywords if kw in resume_lower]
    missing_keywords = [kw for kw in job_keywords if kw not in resume_lower]
    
    # Calculate keyword score - be more lenient for organic resumes
    if job_keywords:
        # Don't penalize too much for missing keywords - focus on quality matches
        keyword_score = (len(found_keywords) / len(job_keywords)) * 100
        # Boost score if at least 40% match (shows relevance without keyword stuffing)
        if keyword_score >= 40:
            keyword_score = min(100, keyword_score * 1.2)
    else:
        keyword_score = 75  # Default if no job description
    
    # Count impact verbs
    impact_verb_count, impact_verbs = count_impact_verbs(resume)
    # Be more forgiving - some roles don't need many action verbs
    impact_score = min(100, (impact_verb_count / 6) * 100)  # Changed from /8 to /6
    
    # Count quantifiable results
    quant_count = count_quantifiable_results(resume)
    quant_score = min(100, (quant_count / 4) * 100)  # Changed from /5 to /4
    
    # Check ATS compatibility
    ats_issues = check_ats_compatibility(resume)
    ats_score = max(0, 100 - (len(ats_issues) * 12))  # Less penalty per issue
    
    # Generate suggestions
    suggestions = generate_suggestions(resume, job_desc, impact_verb_count, quant_count, keyword_score)
    
    # Generate specific line-by-line changes
    specific_changes = generate_specific_changes(resume, job_desc, missing_keywords, impact_verbs)
    
    # Calculate overall score with better weighting
    overall_score = (keyword_score * 0.3 + ats_score * 0.25 + impact_score * 0.25 + quant_score * 0.2)
    
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
        'ats_issues': ats_issues,
        'specific_changes': specific_changes
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🔑 Keywords", "💡 Suggestions", "✏️ Specific Changes", "✅ ATS Check"])
    
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
        
        st.divider()
        st.info("💡 **Pro Tip**: Focus on telling your story naturally. Good resumes balance keywords with authentic achievements. Don't sacrifice readability for keyword density!")
    
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
                    st.write("*Consider incorporating these naturally where relevant:*")
                    for kw in results['missing_keywords']:
                        st.markdown(f'<span class="keyword-missing">✗ {kw}</span>', unsafe_allow_html=True)
                else:
                    st.success("All keywords found!")
            
            st.divider()
            st.warning("⚠️ **Important**: Don't just copy-paste keywords! Incorporate them naturally into your actual experience and skills. Recruiters can tell when a resume is keyword-stuffed.")
        else:
            st.info("📝 Add a job description to see keyword analysis")
    
    with tab3:
        st.subheader("Optimization Suggestions")
        
        if results['suggestions']:
            for suggestion in results['suggestions']:
                st.markdown(f"""
                <div class="suggestion-box suggestion-{suggestion['type']}">
                    <div class="suggestion-title">{suggestion['title']}</div>
                    <div>{suggestion['description']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✨ Your resume looks great! No major suggestions.")
    
    with tab4:
        st.subheader("Specific Line-by-Line Changes")
        
        if results.get('specific_changes'):
            st.write("Here are specific improvements you can make to individual bullet points:")
            st.write("")
            
            for change in results['specific_changes']:
                with st.expander(f"📝 Line {change['line_number']}: {change['original'][:60]}..."):
                    st.markdown(f"**Original:**")
                    st.code(change['original'], language=None)
                    st.markdown(f"**Suggestions:**")
                    for i, suggestion in enumerate(change['suggestions'], 1):
                        st.markdown(f"{i}. {suggestion}")
            
            st.divider()
            st.info("💡 **Remember**: These are suggestions, not requirements. Only make changes that accurately reflect your experience and maintain your authentic voice.")
        else:
            st.success("✨ Your bullet points look well-crafted! No specific changes needed.")
    
    with tab5:
        st.subheader("ATS Compatibility Check")
        
        if results['ats_issues']:
            for issue in results['ats_issues']:
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
                <div>Your resume appears to be well-formatted for Applicant Tracking Systems.</div>
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
