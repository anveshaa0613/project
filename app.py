import streamlit as st
import pdfplumber
import time
from skills import skills_db
from jobs import jobs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="ResumeGlow ✨", page_icon="🌈", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
    color: #1a1a1a;
}
.card {
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
}
.skill {
    display:inline-block;
    padding:6px 12px;
    margin:5px;
    border-radius:12px;
    background:#eee;
}
.center {
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ---------- STATE ----------
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

    st.markdown("<h1>🌈 ResumeGlow ✨</h1>", unsafe_allow_html=True)
    st.write("Turn your resume into career magic 💼")

    st.write("✨ Upload → Analyze → Get Jobs → Apply 🚀")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("🧠 Smart Analysis")
    with col2:
        st.write("💼 Job Matching")
    with col3:
        st.write("🚀 Apply Instantly")

    if st.button("Enter Portal"):
        st.session_state.page = "auth"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- AUTH ----------
elif st.session_state.page == "auth":

    tab1, tab2 = st.tabs(["Login", "Signup"])

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

# ---------- APP ----------
elif st.session_state.page == "app":

    st.sidebar.write(f"👤 {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.page = "home"
        st.rerun()

    file = st.file_uploader("Upload Resume", type="pdf")

    if file:
        with st.spinner("Analyzing..."):
            time.sleep(1)
            results, skills = process_resume(file)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Job Matches")

            for r in results[:3]:
                st.markdown(f"""
                🌟 **{r['role']}** — {r['score']}%  
                👉 [Apply Now]({r['link']})
                """)

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Skills")

            for s in skills:
                st.markdown(f"<span class='skill'>{s}</span>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.balloons()

    else:
        st.info("Upload resume to start")