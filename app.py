# SkillGap - Skill Assessment and Gap Analysis System
# Run with:  streamlit run app.py

from datetime import datetime
import pandas as pd
import streamlit as st

from data_loader import DataLoader
from quiz import QuizGenerator
from analyzer import LevelClassifier, GapAnalyzer, SkillAnalyzer
from database import Database
from auth import AuthService
from history import HistoryReader
from storage import JsonStorage, CsvStorage, MySqlStorage
from charts import ChartBuilder

st.set_page_config(page_title="SkillGap", page_icon="🎯", layout="wide")

with open("style.css") as f:                       # load the design file
    st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)

# ---------- 1. Create the objects ----------
# XAMPP default: user = root, password = empty. Change here if yours is different.
database = Database(host="localhost", user="root", password="", name="skillgap_db", port=3306)

loader = DataLoader("questions.csv", "roles_skills.csv")
quiz_maker = QuizGenerator(loader.questions, loader.roles)
analyzer = SkillAnalyzer(LevelClassifier(), GapAnalyzer())
auth = AuthService(database)
history_reader = HistoryReader(database)
storages = [JsonStorage("results.json"), CsvStorage("history.csv"), MySqlStorage(database)]
charts = ChartBuilder()

# ---------- 2. Memory of the app ----------
# Streamlit runs this file again after every click.
# session_state remembers the values, so the user stays logged in.
if "page" not in st.session_state:
    st.session_state.page = "login"        # login -> welcome -> quiz -> result
    st.session_state.user = None           # None = nobody is logged in
    st.session_state.round = 0
    st.session_state.db_ready = False


def show_banner():
    st.markdown('<div class="hero"><h1>🎯 SkillGap</h1>'
                '<p>Skill Assessment and Gap Analysis System for Students</p></div>',
                unsafe_allow_html=True)


# ---------- 3. Connect to the database ----------
if not st.session_state.db_ready:
    try:
        database.setup()                   # creates the database and tables
        st.session_state.db_ready = True
    except Exception as error:
        show_banner()
        st.error("❌ Cannot connect to MySQL. Open XAMPP and click Start next to MySQL, then refresh this page.")
        st.code(str(error))
        st.stop()                          # stop here, do not show the rest


def go_to(page):
    st.session_state.page = page
    st.rerun()                             # refresh the screen


def start_quiz(role):
    st.session_state.role = role
    st.session_state.quiz = quiz_maker.create_quiz(role)      # random questions
    st.session_state.round = st.session_state.round + 1
    go_to("quiz")


# ---------- 4. Login page (first page) ----------
def show_login():
    show_banner()
    empty1, middle, empty2 = st.columns([1, 2, 1])      # keeps the form in the centre
    with middle:
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                clicked = st.form_submit_button("Login", use_container_width=True)
            if clicked:
                user = auth.login(email.strip(), password)
                if user is None:
                    st.error("Wrong email or password.")
                else:
                    st.session_state.user = user
                    go_to("welcome")

        with tab_register:
            with st.form("register_form"):
                new_name = st.text_input("Full name")
                new_email = st.text_input("Email address")
                new_password = st.text_input("Create password", type="password")
                confirm = st.text_input("Confirm password", type="password")
                clicked = st.form_submit_button("Create Account", use_container_width=True)
            if clicked:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message = auth.register(new_name.strip(), new_email.strip(), new_password)
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)


# ---------- 5. Welcome page ----------
def show_welcome():
    show_banner()
    st.markdown(f"### 👋 Welcome, {st.session_state.user['name']}!")
    st.markdown("#### How it works")
    steps = [["1️⃣", "Select Role", "Choose your target job role"],
             ["2️⃣", "Take Test", "Random objective questions"],
             ["3️⃣", "Get Analysis", "Skill levels and gaps"],
             ["4️⃣", "Improve", "Priority-based learning plan"]]
    cols = st.columns(4)
    for i in range(4):
        icon = steps[i][0]
        title = steps[i][1]
        text = steps[i][2]
        cols[i].markdown(f'<div class="card step"><div class="icon">{icon}</div>'
                         f'<h4>{title}</h4><p>{text}</p></div>', unsafe_allow_html=True)

    st.markdown("#### Available job roles")
    cols = st.columns(2)
    roles = loader.get_role_names()
    for i in range(len(roles)):
        chips = ""
        for skill in loader.get_skills(roles[i]):
            chips = chips + f'<span class="chip">{skill}</span>'
        cols[i % 2].markdown(f'<div class="card"><b>{roles[i]}</b><br>{chips}</div>',
                             unsafe_allow_html=True)
    st.info("👈 Select a role in the sidebar and click Start New Assessment.")


# ---------- 6. Quiz page ----------
def show_quiz():
    show_banner()
    quiz = st.session_state.quiz
    st.markdown(f"### 📝 Assessment for {st.session_state.role}")

    # list of skill names (without repeating)
    skills = []
    for q in quiz:
        if q["skill"] not in skills:
            skills.append(q["skill"])

    tabs = st.tabs(skills)                  # one tab for each skill
    answers = [None] * len(quiz)            # None = not answered yet
    for t in range(len(skills)):
        with tabs[t]:
            for i in range(len(quiz)):
                if quiz[i]["skill"] == skills[t]:
                    answers[i] = st.radio(f"Q{i + 1}. {quiz[i]['question']}",
                                          quiz[i]["options"], index=None,
                                          key=f"q{st.session_state.round}_{i}")

    # count answered questions
    answered = 0
    for a in answers:
        if a is not None:
            answered = answered + 1
    st.progress(answered / len(quiz), text=f"{answered} of {len(quiz)} answered")

    # Submit button works only when all questions are answered
    if st.button("✅ Submit Assessment", disabled=(answered < len(quiz)), use_container_width=True):
        required = loader.get_required_levels(st.session_state.role)
        results = analyzer.analyze(quiz, answers, required)
        record = {"date": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
                  "user_id": st.session_state.user["id"],
                  "name": st.session_state.user["name"],
                  "role": st.session_state.role,
                  "overall_percent": analyzer.overall_percent(results),
                  "results": results}
        for storage in storages:            # save in JSON, CSV and MySQL
            storage.save(record)
        st.session_state.record = record
        go_to("result")


# ---------- 7. Result page ----------
def make_skill_card(r):
    if r["priority"] == "No gap":
        color, label = "ok", "✔ Requirement met"
    elif r["priority"] == "Medium":
        color, label = "mid", "Medium priority"
    else:
        color, label = "high", "High priority"
    return (f'<div class="card"><div class="row"><b>{r["skill"]}</b>'
            f'<span class="badge {color}">{label}</span></div>'
            f'<div class="bar"><div class="fill {color}" style="width:{r["percent"]}%"></div></div>'
            f'<small>Score {r["score"]}/{r["total"]} &nbsp;|&nbsp; Your level: {r["level_name"]}'
            f' &nbsp;|&nbsp; Required: {r["required_name"]}</small></div>')


def show_result():
    show_banner()
    record = st.session_state.record
    results = record["results"]
    percent = record["overall_percent"]

    # top part: donut chart + student details
    left, right = st.columns([1, 2])
    with left:
        st.pyplot(charts.readiness_donut(percent))
    with right:
        st.markdown(f'<div class="card"><small>{record["date"]}</small>'
                    f'<h3 style="margin:4px 0">{record["name"]}</h3>'
                    f'Target role: <b>{record["role"]}</b>'
                    f'<div class="verdict">{analyzer.verdict(percent)}</div></div>',
                    unsafe_allow_html=True)
        met = 0
        for r in results:
            if r["gap"] == 0:
                met = met + 1
        c1, c2, c3 = st.columns(3)
        c1.metric("Skills Assessed", len(results))
        c2.metric("Requirements Met", met)
        c3.metric("Skill Gaps", len(results) - met)

    # skill cards
    st.markdown("### 🎯 Skill-wise Analysis")
    for r in results:
        st.markdown(make_skill_card(r), unsafe_allow_html=True)

    # chart + roadmap
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Your Level vs Required Level")
        st.pyplot(charts.level_comparison(results))
    with col2:
        st.markdown("### 💡 Learning Roadmap")
        number = 1
        for priority in ["High", "Medium"]:           # High priority first
            for r in results:
                if r["priority"] == priority:
                    st.markdown(f'<div class="card"><b>{number}. {r["skill"]}</b><br>'
                                f'<small>{priority} priority — improve from {r["level_name"]} '
                                f'to {r["required_name"]}</small></div>', unsafe_allow_html=True)
                    number = number + 1
        if number == 1:
            st.success("🎉 You meet every requirement for this role.")

    # button
    if st.button("🔄 Retake with new random questions", use_container_width=True):
        start_quiz(st.session_state.role)


# ---------- 8. History page (data comes from MySQL) ----------
def show_history():
    show_banner()
    st.markdown("### 📜 My Previous Assessments")
    rows = history_reader.get_history(st.session_state.user["id"])
    if len(rows) == 0:
        st.info("You have not taken any assessment yet.")
        return

    table_rows = []
    percents = []
    for row in rows:
        table_rows.append([row["role"], str(row["overall_percent"]) + "%",
                           row["taken_on"].strftime("%d-%b-%Y %I:%M %p")])
        percents.insert(0, row["overall_percent"])         # oldest first for the chart
    st.table(pd.DataFrame(table_rows, columns=["Role", "Readiness", "Date"]))

    if len(percents) > 1:
        st.markdown("### 📈 Your Progress")
        st.line_chart(pd.DataFrame({"Readiness %": percents}))


# ---------- 9. Sidebar (only after login) ----------
if st.session_state.user is not None:
    st.sidebar.markdown(f"## 👋 Hello, {st.session_state.user['name']}")
    role = st.sidebar.selectbox("🎓 Target job role", loader.get_role_names())
    if st.sidebar.button("▶ Start New Assessment", use_container_width=True):
        start_quiz(role)
    if st.sidebar.button("📜 My History", use_container_width=True):
        go_to("history")
    if st.sidebar.button("🏠 Home", use_container_width=True):
        go_to("welcome")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        go_to("login")

# ---------- 10. Show the correct page ----------
if st.session_state.user is None:           # not logged in -> always login page
    show_login()
elif st.session_state.page == "welcome":
    show_welcome()
elif st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "result":
    show_result()
elif st.session_state.page == "history":
    show_history()
else:
    show_welcome()