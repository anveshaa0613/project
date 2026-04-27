import streamlit as st
import pdfplumber
import time
from skills import skills_db
from jobs import jobs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ResumePro Elite 💎", page_icon="💎", layout="wide")

# ---------- PREMIUM UI ----------
st.markdown("""
<style>

/* 🌌 Animated Background */
.stApp {
    background: linear-gradient(-45deg, #0d1117, #1e2a4a, #0d1117, #06080d);
    background-size: 400% 400%;
    animation: gradientShift 12s ease infinite;
    color: #f0f6fc;
}

@keyframes gradientShift {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

/* ✨ Glass Cards */
.glass-card {
    background: rgba(23, 28, 36, 0.5);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* 🌈 Gradient Text */
.highlight {
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* 🚀 Buttons */
.stButton>button {
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    border-radius: 14px;
    color: white;
    font-weight: bold;
}

/* 🎯 Center */
.center {
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
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

# ---------- HOME ----------
if st.session_state.page == "home":

    st.markdown("<div class='center'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 style='font-size:70px;'>Next-Gen <span class='highlight'>Career AI</span></h1>
    <p style='font-size:22px;'>Upload your resume & unlock job opportunities 🚀</p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("🧠 AI Analysis")
    with col2:
        st.write("💼 Smart Matching")
    with col3:
        st.write("🚀 Apply Instantly")

    if st.button("🚀 ENTER PORTAL"):
        st.session_state.page = "auth"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- AUTH ----------
elif st.session_state.page == "auth":

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])

    with tab1:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user in st.session_state.users and st.session_state.users[user]["pass"] == pwd:
                st.session_state.user = user
                st.session_state.page = "app"
                st.rerun()
            else:
                st.error("Wrong details")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            st.session_state.users[new_user] = {"pass": new_pass}
            st.success("Account created")

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- APP ----------
elif st.session_state.page == "app":

    st.sidebar.write(f"👤 {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("<h2>✨ Command Center</h2>", unsafe_allow_html=True)

    file = st.file_uploader("📄 Upload Resume", type="pdf")

    if file:
        with st.spinner("🔮 Analyzing..."):
            time.sleep(1.5)
            results, skills = process_resume(file)

        col1, col2 = st.columns([2,1])

        # JOBS
        with col1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.write("### 🎯 Job Matches")

            for r in results[:3]:
                st.write(f"**{r['role']}**")
                st.progress(r['score']/100)
                st.markdown(f"👉 [Apply Now 🚀]({r['link']})")

            st.markdown("</div>", unsafe_allow_html=True)

        # SKILLS
        with col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.write("### 🧠 Skills Found")

            for s in skills:
                st.markdown(f"- {s}")

            st.markdown("</div>", unsafe_allow_html=True)

        st.balloons()

    else:
        st.info("Upload resume to begin 🚀")