import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io

def display_results(results):
    st.subheader("📊 Results")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Resume 1 Match", f"{results['score1'] * 100:.1f}%")
        st.success(f"Matched Skills: {', '.join(results['matched_skills_1']) or 'None'}")
        st.error(f"Missing Skills: {', '.join(results['missing_skills_1']) or 'None'}")
        st.write(f"Resume 1 - {len(results['matched_skills_1'])} matched, {len(results['missing_skills_1'])} missing")
    with col2:
        st.metric("Resume 2 Match", f"{results['score2'] * 100:.1f}%")
        st.success(f"Matched Skills: {', '.join(results['matched_skills_2']) or 'None'}")
        st.error(f"Missing Skills: {', '.join(results['missing_skills_2']) or 'None'}")
        st.write(f"Resume 2 - {len(results['matched_skills_2'])} matched, {len(results['missing_skills_2'])} missing")

    st.markdown("### 📌 Summary")
    st.info(results['summary'])

    st.markdown("### 📈 Bar Chart Comparison")
    plot_bar_comparison(results['score1'], results['score2'])

    st.markdown("### 🧠 Skill Match Pie Charts")
    skill_col1, skill_col2 = st.columns(2)
    with skill_col1:
        st.markdown("#### Resume 1")
        plot_pie_chart(results['matched_skills_1'], results['missing_skills_1'], "Resume 1")
    with skill_col2:
        st.markdown("#### Resume 2")
        plot_pie_chart(results['matched_skills_2'], results['missing_skills_2'], "Resume 2")

    st.markdown("### 💡 Recommendations")
    st.markdown(generate_recommendations(results))

    

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

# ------------------ Main ------------------
if "score1" in st.session_state and "score2" in st.session_state:
    results_data = {
        "score1": st.session_state["score1"],
        "score2": st.session_state["score2"],
        "matched_skills_1": st.session_state.get("matched_skills_1", []),
        "missing_skills_1": st.session_state.get("missing_skills_1", []),
        "matched_skills_2": st.session_state.get("matched_skills_2", []),
        "missing_skills_2": st.session_state.get("missing_skills_2", []),
        "summary": st.session_state.get("summary", "No summary available.")
    }
    display_results(results_data)

    report_txt = create_downloadable_report(results_data)
    st.download_button("📥 Download Report as TXT", data=report_txt, file_name="resume_comparison.txt")

else:
    st.error("🚫 No results to display. Please compare resumes from the Home page first.")
