import streamlit as st
import pdfplumber
import time
from skills import skills_db
from jobs import jobs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ResumeGlow ✨", page_icon="🌈", layout="wide")

# ---------- IMPROVED UI ----------
st.markdown("""
<style>

/* 🌈 Soft aesthetic background */
.stApp {
    background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
    color: #1a1a1a;
}

/* 📦 Cards */
.card {
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

/* 💅 Buttons */
.stButton>button {
    background: linear-gradient(90deg,#ff6ec4,#7873f5);
    color: white;
    border-radius: 12px;
    font-weight: bold;
}

/* 🏷️ Skills */
.skill {
    display:inline-block;
    padding:6px 12px;
    margin:5px;
    border-radius:12px;
    background:#eee;
    color:#333;
    font-size:12px;
    font-weight:bold;
}

/* 🎯 Center */
.center {
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
if "users" not in st.session_state:
    st.session_state.users = {"user1": {"pass": "123"}}

if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------- LOGIC ----------
def process_resume(file):
    with pdfplumber.open(file) as pdf:
        text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

    skills = [s for s in skills_db if s.lower() in text.lower()]
    job_texts = [j["skills"] for j in jobs]

    tfidf = TfidfVectorizer().fit_transform([text] + job_texts)
    scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

    results = []
    for i, s in enumerate(scores):
        results.append({
            "role": jobs[i]["role"],
            "score": round(s * 100, 1),
            "link": jobs[i]["link"]
        })

    return sorted(results, key=lambda x: x["score"], reverse=True), skills

# ---------- HOME PAGE ----------
if st.session_state.page == "home":

    st.markdown("<div class='center'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 style='font-size:70px;'>🌈 ResumeGlow ✨</h1>
    <p style='font-size:22px;'>
    Turn your resume into <b>career magic</b> 💼💖
    </p>
    """, unsafe_allow_html=True)

    st.write("✨ Upload → Analyze → Get Jobs → Apply instantly 🚀")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🧠 Smart Analysis")
        st.write("Extracts your skills automatically")

    with col2:
        st.markdown("### 💼 Job Matching")
        st.write("Finds best jobs using AI")

    with col3:
        st.markdown("### 🚀 Apply Instantly")
        st.write("Direct links to job platforms")

    st.markdown("---")

    st.info("💡 Tip: Use a resume with clear skills for better results!")

    if st.button("✨ Enter Portal"):
        st.session_state.page = "auth"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- AUTH ----------
elif st.session_state.page == "auth":

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])

    with tab1:
        user = st.text_input("👤 Username")
        pwd = st.text_input("🔑 Password", type="password")

        if st.button("Login"):
            if user in st.session_state.users and st.session_state.users[user]["pass"] == pwd:
                st.session_state.user = user
                st.session_state.page = "app"
                st.rerun()
            else:
                st.error("❌ Wrong details")

    with tab2:
        new_user = st.text_input("✨ New Username")
        new_pass = st.text_input("🔐 New Password", type="password")

        if st.button("Create Account"):
            st.session_state.users[new_user] = {"pass": new_pass}
            st.success("🎉 Account created!")

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- MAIN APP ----------
elif st.session_state.page == "app":

    st.sidebar.write(f"👤 {st.session_state.user}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.page = "home"
        st.rerun()

    st.title("💼 Career Dashboard ✨")

    file = st.file_uploader("📄 Upload your Resume", type="pdf")

    if file:
        with st.spinner("🔮 Analyzing your resume..."):
            time.sleep(1)
            results, skills = process_resume(file)

        col1, col2 = st.columns([2, 1])

        # JOB MATCHES
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### 💼 Job Matches")

            for r in results[:3]:
                st.markdown(f"""
                🌟 **{r['role']}** — {r['score']}% match  
                👉 [Apply Now 🚀]({r['link']})
                """)

            st.markdown("</div>", unsafe_allow_html=True)

        # SKILLS
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### 🧠 Your Skills")

            for s in skills:
                st.markdown(f"<span class='skill'>{s}</span>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.balloons()

    else:
        st.info("✨ Upload a resume to start your glow-up")