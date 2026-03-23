# Resume Optimizer - Streamlit App

AI-powered resume analysis and optimization tool built with Streamlit.

## Features

- 📄 **Resume Upload**: Support for TXT files or paste text directly
- 🎯 **Job Description Matching**: Compare resume against job postings
- 📊 **Multi-Dimensional Scoring**: Overall score, keywords, ATS compatibility, impact verbs, and quantifiable results
- 💡 **Smart Suggestions**: Actionable improvement recommendations
- ✅ **ATS Compatibility Check**: Identify formatting issues that may block ATS systems

## Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Deploy to Streamlit Cloud (Free!)

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `resume-optimizer`
3. Make it public (required for free Streamlit Cloud hosting)

### Step 2: Upload Files

Upload these files to your repository:
- `app.py` (the main Streamlit application)
- `requirements.txt` (dependencies)
- `README.md` (this file - optional)

You can do this by:
- **Option A**: Drag and drop files on GitHub web interface
- **Option B**: Use git commands:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-optimizer.git
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/resume-optimizer`
5. Set main file path: `app.py`
6. Click "Deploy!"

Your app will be live at: `https://YOUR_USERNAME-resume-optimizer.streamlit.app`

### Step 4: Share Your App! 🚀

Once deployed, you'll get a public URL you can share with anyone. The app will auto-update whenever you push changes to GitHub.

## Usage

1. **Upload or paste** your resume text in the sidebar
2. (Optional) Add a **job description** for tailored keyword analysis
3. Click **"Analyze Resume"**
4. Review your results across 4 tabs:
   - **Overview**: Performance metrics and quick insights
   - **Keywords**: Found vs missing keywords from job description
   - **Suggestions**: Personalized improvement recommendations
   - **ATS Check**: Formatting compatibility issues

## How It Works

The analyzer evaluates your resume across multiple dimensions:

- **Keyword Matching**: Extracts keywords from job description and checks presence in resume
- **Impact Verbs**: Counts action verbs like "achieved," "led," "developed"
- **Quantifiable Results**: Identifies metrics, percentages, and numbers
- **ATS Compatibility**: Checks for common formatting issues (tabs, special characters, section headers)
- **Overall Score**: Weighted average of all metrics

## Privacy

All analysis happens **locally** in your browser session. No data is stored or transmitted to external servers.

## Customization

You can easily customize the analyzer by editing `app.py`:

- Add more impact verbs in the `count_impact_verbs()` function
- Adjust scoring weights in the `analyze_resume()` function
- Add new suggestion rules in `generate_suggestions()`
- Customize the UI colors and styling in the CSS section

## License

MIT License - Feel free to use and modify!
