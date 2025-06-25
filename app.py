import streamlit as st
import PyPDF2
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ------------------ Constants for Navigation ------------------
HOME_PAGE = "🏠 Home"
RESULTS_PAGE = "📊 Results"
LOGOUT_PAGE = "🚪 Logout"

# ------------------ Page Config ------------------
APP_TITLE = "AI-Powered Resume Screening"
st.set_page_config(page_title=APP_TITLE, layout="wide")

# ------------------ Custom CSS Styling ------------------
st.markdown("""
    <style>
        .main { background-color: #f0f2f6; }
        .block-container { padding: 2rem 3rem; }
        .stButton>button, .stDownloadButton>button {
            background-color: #4CAF50; color: white; border: none;
            padding: 10px 20px; border-radius: 8px; font-weight: bold;
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            background-color: #ffffff; border-radius: 8px;
        }
        /* Login container styling */
        .login-container {
            max-width: 400px;
            margin: 80px auto;
            padding: 30px;
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-radius: 12px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-container h1 {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 20px;
            font-weight: 700;
        }
        .login-container .stTextInput > div > div > input {
            border-radius: 8px !important;
            padding: 10px;
            border: 1.5px solid #ddd !important;
            font-size: 16px;
        }
        .login-container .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 12px 0 !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            margin-top: 15px;
            width: 100%;
            cursor: pointer;
        }
        .login-container .stText > div > label {
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ Helper Functions ------------------
def read_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return " ".join([page.extract_text() or "" for page in reader.pages])
    else:
        return file.read().decode("utf-8")

def extract_skills_from_jd(jd_text, known_skills):
    jd_text = jd_text.lower()
    jd_skills = [skill for skill in known_skills if skill in jd_text]
    return jd_skills

def extract_skills(text, skill_list):
    text = text.lower()
    found = [skill for skill in skill_list if skill in text]
    missing = [skill for skill in skill_list if skill not in text]
    return found, missing

def plot_bar_comparison(score1, score2):
    df = pd.DataFrame({"Resume": ["Resume 1", "Resume 2"], "Match Score": [score1 * 100, score2 * 100]})
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=df, x="Resume", y="Match Score", palette=["#4CAF50", "#1976D2"], ax=ax)
    ax.set_title("Resume Match Comparison")
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%')
    st.pyplot(fig)

def plot_pie_chart(matched, missing, title):
    total = len(matched) + len(missing)
    if total == 0:
        st.write("No skills available to show chart.")
        return

    labels = [f'Matched ({len(matched)})', f'Missing ({len(missing)})']
    sizes = [len(matched), len(missing)]
    colors = ['#4CAF50', '#FF6F61']

    fig, ax = plt.subplots()
    _, _, _ = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10}
    )
    ax.axis('equal')
    ax.set_title(f"{title} Skill Match")

    st.markdown(f"**Matched Skills ({len(matched)}):** {', '.join(matched) or 'None'}")
    st.markdown(f"**Missing Skills ({len(missing)}):** {', '.join(missing) or 'None'}")

    st.pyplot(fig)

def generate_recommendations(results):
    recommendations = []

    for i in [1, 2]:
        missing = results[f'missing_skills_{i}']
        if missing:
            recommendations.append(f"**Resume {i}:** Consider adding these missing skills: *{', '.join(missing)}*.")
        else:
            recommendations.append(f"**Resume {i}:** All key job skills are covered. Great job!")

    if results['score1'] > results['score2']:
        recommendations.append("✅ **Resume 1 is a better match based on skills and similarity.**")
    elif results['score2'] > results['score1']:
        recommendations.append("✅ **Resume 2 is a better match based on skills and similarity.**")
    else:
        recommendations.append("🔄 **Both resumes have similar match scores.**")

    return "\n\n".join(recommendations)

def create_downloadable_report(results):
    report = f"""
📊 Resume Screening Report

Resume 1 Match: {results['score1'] * 100:.1f}%
Matched Skills: {', '.join(results['matched_skills_1']) or 'None'}
Missing Skills: {', '.join(results['missing_skills_1']) or 'None'}

Resume 2 Match: {results['score2'] * 100:.1f}%
Matched Skills: {', '.join(results['matched_skills_2']) or 'None'}
Missing Skills: {', '.join(results['missing_skills_2']) or 'None'}

📌 Summary:
{results['summary']}

💡 Recommendations:
{generate_recommendations(results)}
"""
    return report

# ------------------ Login Function ------------------
def login():
    st.markdown("""
    <div class="login-container">
        <h1>🔐 Login</h1>
        <p>Welcome to the AI-Powered Resume Screening System. Please log in to continue.</p>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if username in st.session_state["users"] and st.session_state["users"][username] == password:
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
                st.success(f"Welcome, {username}! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Session State Setup ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123", "tejal": "tejal@2025"}
if "user" not in st.session_state:
    st.session_state.user = None

# ------------------ Known Skills List ------------------
known_skills = [
    # Frontend & Web
    "html", "css", "scss", "sass", "javascript", "typescript", "react", "redux", 
    "next.js", "vue.js", "angular", "bootstrap", "tailwind css", "jquery", 
    "responsive design", "web accessibility", "ui/ux", "figma", "adobe xd",

    # Backend & Core Programming
    "java", "spring", "spring boot", "hibernate", "rest api", "restful apis", 
    "microservices", "servlets", "jsp", "sql", "mysql", "postgresql", "mongodb", 
    "oracle", "node.js", "express.js", "php", "c", "c++", "c#", ".net", "flask", "django",

    # Android Development
    "android", "kotlin", "java for android", "android studio", "xml", "firebase", 
    "retrofit", "room", "jetpack", "mvvm", "mvp", "jetpack compose", "google maps api", 
    "material design", "rest", "json", "application design", "application development", 
    "play store deployment", "android sdk", "lifecycle management",

    # DevOps & Cloud
    "git", "github", "gitlab", "bitbucket", "jenkins", "docker", "kubernetes", 
    "aws", "gcp", "azure", "ci/cd", "terraform", "ansible", "helm", "monitoring", 
    "grafana", "prometheus", "logstash", "devops tools",

    # Data Science & Machine Learning
    "python", "r", "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn", 
    "tensorflow", "pytorch", "keras", "xgboost", "lightgbm", "mlops", "mlflow", 
    "airflow", "data preprocessing", "model evaluation", "feature engineering",

    # NLP
    "nlp", "text preprocessing", "nltk", "spacy", "transformers", "bert", "gpt", 
    "hugging face", "langchain", "text classification", "sentiment analysis", 
    "topic modeling", "ner", "text summarization",

    # Tools & Platforms
    "jupyter", "colab", "vs code", "pycharm", "eclipse", "intellij", 
    "postman", "swagger", "docker hub", "heroku", "netlify", "streamlit", 

    # BI & Analytics
    "power bi", "tableau", "excel", "data visualization", "data analysis", 
    "dash", "looker", "metabase", "superset",

    # Software Engineering Practices
    "agile", "scrum", "jira", "confluence", "uml", "software development lifecycle",
    "system design", "api design", "unit testing", "integration testing", "test cases",

    # Soft Skills / Misc
    "problem solving", "communication", "teamwork", "critical thinking", 
    "debugging", "adaptability", "leadership", "collaboration", 
    "time management", "presentation", "analytical thinking", "creativity"
]


# ------------------ Main Application ------------------
if st.session_state.logged_in:
    with st.sidebar:
        st.title("🧭 Menu")
        st.markdown(f"👤 Logged in as: **{st.session_state.user}**")
        nav_choice = st.radio("Select a Page:", [HOME_PAGE, RESULTS_PAGE, LOGOUT_PAGE], index=[HOME_PAGE, RESULTS_PAGE, LOGOUT_PAGE].index(st.session_state.get("nav_choice", HOME_PAGE)))


    if nav_choice == HOME_PAGE:
        st.title("📝 Resume Screening System")
        st.markdown("#### Empowering Recruiters with Smart Resume Comparisons")

        job_desc = st.text_area("📋 Paste Job Description Here", height=150)

        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📎 Resume 1")
            resume1_file = st.file_uploader("Upload Resume 1", type=["pdf", "txt"], key="resume1")
        with col2:
            st.write("### 📎 Resume 2")
            resume2_file = st.file_uploader("Upload Resume 2", type=["pdf", "txt"], key="resume2")

        if st.button("🔍 Compare Resumes"):
            if not job_desc.strip() or not resume1_file or not resume2_file:
                st.error("Please provide all required inputs: Job Description and both resumes.")
            else:
                resume1_text = read_file(resume1_file)
                resume2_text = read_file(resume2_file)

                # Extract relevant JD skills dynamically
                jd_skills = extract_skills_from_jd(job_desc, known_skills)

                # Extract matched and missing skills from resumes based on JD skills
                matched_skills_1, missing_skills_1 = extract_skills(resume1_text, jd_skills)
                matched_skills_2, missing_skills_2 = extract_skills(resume2_text, jd_skills)

                # Calculate match percentage based on JD skills only
                score1 = round(len(matched_skills_1) / len(jd_skills), 2) if jd_skills else 0
                score2 = round(len(matched_skills_2) / len(jd_skills), 2) if jd_skills else 0

                # Store results in session_state
                st.session_state["score1"] = score1
                st.session_state["score2"] = score2
                st.session_state["matched_skills_1"] = matched_skills_1
                st.session_state["missing_skills_1"] = missing_skills_1
                st.session_state["matched_skills_2"] = matched_skills_2
                st.session_state["missing_skills_2"] = missing_skills_2
                st.session_state["jd_skills"] = jd_skills

                # Summary
                if score1 > score2:
                    summary = f"Resume 1 has better skill alignment ({score1*100:.0f}%)."
                elif score2 > score1:
                    summary = f"Resume 2 has better skill alignment ({score2*100:.0f}%)."
                else:
                    summary = f"Both resumes are similarly aligned ({score1*100:.0f}%)."
                st.session_state["summary"] = summary
                st.session_state["nav_choice"] = RESULTS_PAGE
                st.rerun()

    elif nav_choice == RESULTS_PAGE:
        if "score1" in st.session_state and "score2" in st.session_state:
            st.title("📊 Resume Comparison Results")
            st.markdown(f"### Job Description Skills: {', '.join(st.session_state.get('jd_skills', []))}")

            results_data = {
                "score1": st.session_state.score1,
                "score2": st.session_state.score2,
                "matched_skills_1": st.session_state.matched_skills_1,
                "missing_skills_1": st.session_state.missing_skills_1,
                "matched_skills_2": st.session_state.matched_skills_2,
                "missing_skills_2": st.session_state.missing_skills_2,
                "summary": st.session_state.summary,
            }

            # Display metrics, summaries, charts & recommendations
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Resume 1 Match", f"{results_data['score1']*100:.1f}%")
                st.success(f"Matched Skills: {', '.join(results_data['matched_skills_1']) or 'None'}")
                st.error(f"Missing Skills: {', '.join(results_data['missing_skills_1']) or 'None'}")
            with col2:
                st.metric("Resume 2 Match", f"{results_data['score2']*100:.1f}%")
                st.success(f"Matched Skills: {', '.join(results_data['matched_skills_2']) or 'None'}")
                st.error(f"Missing Skills: {', '.join(results_data['missing_skills_2']) or 'None'}")

            st.markdown("### 📌 Summary")
            st.info(results_data['summary'])

            st.markdown("### 📈 Bar Chart Comparison")
            plot_bar_comparison(results_data['score1'], results_data['score2'])

            st.markdown("### 🧠 Skill Match Pie Charts")
            skill_col1, skill_col2 = st.columns(2)
            with skill_col1:
                st.markdown("#### Resume 1")
                plot_pie_chart(results_data['matched_skills_1'], results_data['missing_skills_1'], "Resume 1")
            with skill_col2:
                st.markdown("#### Resume 2")
                plot_pie_chart(results_data['matched_skills_2'], results_data['missing_skills_2'], "Resume 2")

            st.markdown("### 💡 Recommendations")
            st.write(generate_recommendations(results_data))

            report = create_downloadable_report(results_data)
            st.download_button("📥 Download Report as TXT", report, file_name="resume_screening_report.txt")

        else:
            st.warning("No results to display. Please upload resumes and job description, then compare.")

    elif nav_choice == LOGOUT_PAGE:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

else:
    login()
