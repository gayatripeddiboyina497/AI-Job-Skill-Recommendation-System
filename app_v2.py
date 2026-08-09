import streamlit as st
import pandas as pd

# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="AI Job Skill Recommendation System",
    page_icon="🎯",
    layout="wide"
)

# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data

def load_data():
    df = pd.read_csv(
        "data/raw/data_science_job_posts_2025.csv"
    ) 
    return df


df = load_data()

# ============================================================
# SKILL EXTRACTION
# ============================================================

skills = (
    df["skills"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
)

skill_counts = skills.value_counts()

# ============================================================
# ROLE-WISE SKILL DATA
# ============================================================

role_skill_data = {}

for role in df["job_title"].dropna().unique():

    role_data = df[
        df["job_title"].str.lower() == role.lower()
    ]

    role_skills = (
        role_data["skills"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
    )

    role_skill_data[role] = role_skills.value_counts()

# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def recommend_for_role(job_role, current_skills, top_n=10):

    job_role = job_role.strip().lower()

    current_skills = [
        skill.strip().lower()
        for skill in current_skills.split(",")
        if skill.strip()
    ]

    matching_role = None

    for role in role_skill_data.keys():

        if role.strip().lower() == job_role:

            matching_role = role
            break

    if matching_role is None:

        return pd.DataFrame(
            columns=[
                "Skill",
                "Job Demand",
                "Demand %",
                "Priority"
            ]
        )

    role_skills = role_skill_data[matching_role]

    total_role_jobs = df[
        df["job_title"].str.lower()
        == matching_role.lower()
    ].shape[0]

    recommendations = []

    for skill, demand in role_skills.items():

        if skill.lower() not in current_skills:

            demand_percentage = round(
                (demand / total_role_jobs) * 100,
                2
            )

            if demand_percentage >= 50:

                priority = "🔥 High"

            elif demand_percentage >= 20:

                priority = "⭐ Medium"

            else:

                priority = "✅ Low"

            recommendations.append(
                {
                    "Skill": skill,
                    "Job Demand": demand,
                    "Demand %": demand_percentage,
                    "Priority": priority
                }
            )

        if len(recommendations) == top_n:
            break

    return pd.DataFrame(recommendations)

# ============================================================
# READINESS SCORE
# ============================================================

def calculate_readiness(job_role, current_skills):

    job_role = job_role.strip().lower()

    current_skills = [
        skill.strip().lower()
        for skill in current_skills.split(",")
        if skill.strip()
    ]

    matching_role = None

    for role in role_skill_data.keys():

        if role.strip().lower() == job_role:

            matching_role = role
            break

    if matching_role is None:
        return 0

    role_skills = role_skill_data[matching_role]

    if len(role_skills) == 0:
        return 0

    matched_skills = sum(
        1
        for skill in role_skills.index
        if skill.lower() in current_skills
    )

    score = (
        matched_skills /
        len(role_skills)
    ) * 100

    return round(score, 2)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎯 Navigation")

st.sidebar.markdown(
    """
    ### AI Job Skill Recommendation

    This system analyzes real-world
    data science job postings.

    **Features**

    • Personalized skill recommendations

    • Job demand analysis

    • Skill priority levels

    • Career readiness score

    • Downloadable recommendations
    """
)

# ============================================================
# MAIN TITLE
# ============================================================

st.title("🎯 AI Job Skill Recommendation System")

st.markdown(
    """
    ### Find the skills you need for your target career

    Select your target job role and enter your current
    skills. The system analyzes job-market demand and
    recommends the most important skills you should learn.
    """
)

st.divider()

# ============================================================
# USER INPUT
# ============================================================

st.header("👤 Enter Your Details")

available_roles = sorted(
    role_skill_data.keys(),
    key=lambda x: x.lower()
)

job_role = st.selectbox(
    "🎯 Select Target Job Role",
    available_roles
)

current_skills = st.text_input(
    "💻 Enter Your Current Skills",
    placeholder="Example: Python, SQL, Excel"
)

# ============================================================
# RECOMMEND BUTTON
# ============================================================

if st.button(
    "🚀 Recommend Skills",
    width="stretch"
):

    if current_skills.strip() == "":

        st.warning(
            "⚠️ Please enter at least one skill."
        )

    else:

        recommendations = recommend_for_role(
            job_role,
            current_skills,
            top_n=10
        )

        readiness = calculate_readiness(
            job_role,
            current_skills
        )

        st.session_state["recommendations"] = recommendations
        st.session_state["readiness"] = readiness
        st.session_state["role"] = job_role

# ============================================================
# RESULTS
# ============================================================

if "recommendations" in st.session_state:

    recommendations = (
        st.session_state["recommendations"]
    )

    readiness = st.session_state["readiness"]

    selected_role = st.session_state["role"]

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    st.header("📈 Career Readiness")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Target Role",
            selected_role.title()
        )

    with col2:

        st.metric(
            "Readiness Score",
            f"{readiness}%"
        )

    with col3:

        st.metric(
            "Recommended Skills",
            len(recommendations)
        )

    st.progress(
        min(readiness / 100, 1.0)
    )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.header("🎯 Recommended Skills")

    if recommendations.empty:

        st.success(
            "🎉 You already have the important skills "
            "identified for this role!"
        )

    else:

        st.dataframe(
            recommendations,
            width="stretch",
            hide_index=True
        )

        # ----------------------------------------------------
        # SKILL DEMAND CHART
        # ----------------------------------------------------

        st.header("📊 Skill Demand")

        chart_data = recommendations.set_index(
            "Skill"
        )["Job Demand"]

        st.bar_chart(chart_data)

        # ----------------------------------------------------
        # CAREER TIPS
        # ----------------------------------------------------

        st.header("💡 Career Development Tips")

        st.info(
            """
            ✔ Learn High Priority skills first.

            ✔ Practice using real-world datasets.

            ✔ Build 2–3 data science projects.

            ✔ Add projects to your resume.

            ✔ Practice SQL and Python regularly.

            ✔ Prepare for technical interviews.
            """
        )

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        csv = recommendations.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Recommendations",
            data=csv,
            file_name="recommended_skills.csv",
            mime="text/csv"
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center">

    <h4>🎯 AI Job Skill Recommendation System</h4>

    <p>Final Year BSc Data Science Project</p>

    <p>Python • Pandas • Streamlit</p>

    </div>
    """,
    unsafe_allow_html=True
)