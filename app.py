import streamlit as st
import pandas as pd
import random
import time
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Aptitude Quiz", layout="centered")

# =========================
# LOAD CSS
# =========================
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
logo_container = st.container()

with logo_container:
    st.image("assets/logo.png", width=140)
# =========================
# SESSION STATE DEFAULTS
# =========================
defaults = {
    "page": "setup",
    "questions": [],
    "current_index": 0,
    "score": 0,
    "wrong": 0,
    "skipped": 0,
    "start_time": None,
    "time_limit": None,
    "mode": None,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =========================
# LOAD CSV
# =========================
def load_csv(file_path, topic_name):
    df = pd.read_csv(file_path)
    df.columns = [c.strip().lower() for c in df.columns]

    questions_list = []
    for _, row in df.iterrows():
        options_dict = {
            "A": row['option a'],
            "B": row['option b'],
            "C": row['option c'],
            "D": row['option d']
        }
        correct_letter = str(row['answer']).strip().upper()
        correct_answer_text = options_dict.get(correct_letter, "")
        q = {
            "topic": topic_name,
            "question": row['question'],
            "options": list(options_dict.values()),
            "answer": correct_answer_text
        }
        questions_list.append(q)
    return questions_list

# =========================
# LOAD DATASETS
# =========================
all_questions = []
all_questions += load_csv("data/cse_dataset.csv", "CSE / Technical")
all_questions += load_csv("data/clean_general_aptitude_dataset.csv", "General Aptitude")
all_questions += load_csv("data/logical_reasoning_questions.csv", "Logical Reasoning")

# =========================
# AI QUESTION GENERATION
# =========================
def generate_ai_questions(pool, n=20):
    ai_questions = []

    if len(pool) == 0:
        return []

    sample_questions = random.sample(pool, min(n, len(pool)))

    for q in sample_questions:
        new_q_text = q["question"].replace("1", str(random.randint(2, 9)))

        options = q["options"].copy()
        correct_answer = q["answer"]
        random.shuffle(options)

        ai_q = {
            "topic": q["topic"] + " (AI)",
            "question": new_q_text,
            "options": options,
            "answer": correct_answer
        }

        ai_questions.append(ai_q)

    return ai_questions

# =========================
# START / RESTART QUIZ
# =========================
def start_quiz(selected_topic="Jumbled"):
    if selected_topic == "Jumbled":
        filtered = all_questions.copy()
    else:
        filtered = [q for q in all_questions if q["topic"] == selected_topic]

    # Generate AI questions ONLY from selected topic
    ai_questions = generate_ai_questions(filtered, n=10)

    filtered += ai_questions
    random.shuffle(filtered)

    st.session_state.questions = filtered[:20]
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.wrong = 0
    st.session_state.skipped = 0
    st.session_state.time_limit = 120 if st.session_state.mode == "Quick Mode" else 300
    st.session_state.start_time = time.time()
    st.session_state.page = "quiz"
    st.rerun()
    
def restart_quiz():
    st.session_state.clear()
    st.rerun()

# =========================
# PAGE 1 — SETUP
# =========================
if st.session_state.page == "setup":
    # =========================
    # GLOBAL HEADER
    # =========================
    st.markdown('<div class="global-header">🧠 AI Aptitude Mastery</div>', unsafe_allow_html=True)


    # =========================
    # GLASS CARD TITLE
    # =========================
    st.markdown('''
    <div class="glass-card">
        <div class="glass-title">Pick Your Challenge</div>
    </div>
    ''', unsafe_allow_html=True)


    # =========================
    # MODE SELECTION CARDS
    # =========================
    st.markdown('<div class="mode-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        quick_selected = "selected" if st.session_state.mode == "Quick Mode" else ""
        st.markdown(f"""
            <div class='mode-card {quick_selected}'>
                <div class='mode-title'>⚡ Quick Play Mode</div>
                <div class='mode-desc'>2 Minutes • Blink and Solve</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Quick Mode", key="quick"):
            st.session_state.mode = "Quick Mode"

    with col2:
        full_selected = "selected" if st.session_state.mode == "Pro Mode" else ""
        st.markdown(f"""
            <div class='mode-card {full_selected}'>
                <div class='mode-title'>🎯 Pro Play Mode</div>
                <div class='mode-desc'>5 Minutes • Think, don't Blink</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Pro Mode", key="full"):
            st.session_state.mode = "Pro Mode"

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # TOPIC SELECTION
    # =========================
    selected_topic = st.selectbox(
        "Select Topic / Jumbled Mode",
        ["Jumbled", "CSE / Technical", "General Aptitude", "Logical Reasoning"]
    )

    # =========================
    # START QUIZ BUTTON
    # =========================
    if st.session_state.mode and st.button("🚀 Start Quiz"):
        start_quiz(selected_topic)
        


# =========================
# PAGE 2 — QUIZ
# =========================
elif st.session_state.page == "quiz":
    st_autorefresh(interval=1000, key="timer")
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = int(st.session_state.time_limit - elapsed_time)

    if remaining_time <= 0 or st.session_state.current_index >= len(st.session_state.questions):
        st.session_state.page = "result"
        st.rerun()

    minutes = remaining_time // 60
    seconds = remaining_time % 60

    st.markdown('''
<div class="glass-card">
    <div class="glass-title">Think Quick, Act Smart!</div>
</div>
''', unsafe_allow_html=True)
    st.subheader(f"⏳ Time Remaining: {minutes:02d}:{seconds:02d}")
    st.progress(remaining_time / st.session_state.time_limit)

    q = st.session_state.questions[st.session_state.current_index]
    st.markdown("---")
    st.subheader(f"Question {st.session_state.current_index + 1}")
    st.write(f"({q['topic']})")
    st.write(q["question"])

    selected_option = st.radio(
    "Choose an option:",
    q["options"],
    index=None,  
    key=f"answer_{st.session_state.current_index}"
)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("☑️ Submit"):
            if selected_option == q["answer"]:
                st.session_state.score += 1
            else:
                st.session_state.wrong += 1
            st.session_state.current_index += 1
            st.rerun()

    with col2:
        if st.button("⏭ Skip"):
            st.session_state.skipped += 1
            st.session_state.current_index += 1
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PAGE 3 — RESULT
# =========================
elif st.session_state.page == "result":
    st.markdown('<div class="global-header">📚 Performance Dashboard</div>', unsafe_allow_html=True)
    st.markdown('''
<div class="glass-card">
    <div class="glass-title">"Your Brain Just Got Stronger🤘🏻"</div>
</div>
''', unsafe_allow_html=True)
    correct = st.session_state.score
    wrong = st.session_state.wrong
    skipped = st.session_state.skipped
    attempted = correct + wrong
    elapsed_time = time.time() - st.session_state.start_time
    accuracy = (correct / attempted * 100) if attempted > 0 else 0

    IQ_score = 80 + (correct * 3) - (wrong * 1) - (elapsed_time / 10)
    IQ_score = max(70, min(140, int(IQ_score)))

    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", correct)
    col2.metric("Wrong", wrong)
    col3.metric("Skipped", skipped)
    st.metric("Accuracy (%)", f"{accuracy:.2f}%")

    # =========================
    # RAINBOW SPEEDOMETER
    # =========================
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=IQ_score,
        title={'text': "Predicted IQ Score"},
        gauge={
            'axis': {'range': [70, 140]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [70, 90], 'color': "#ff4b4b"},
                {'range': [90, 100], 'color': "#ff914d"},
                {'range': [100, 120], 'color': "#ffd93d"},
                {'range': [120, 130], 'color': "#6bcf63"},
                {'range': [130, 140], 'color': "#4d96ff"},
            ],
        }
    ))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    if IQ_score >= 120:
        st.success("🏆 IQ Level: Expert")
    elif IQ_score >= 100:
        st.info("📘 IQ Level: Intermediate")
    else:
        st.warning("😔 IQ Level: Beginner")

    if st.button("🔄 Restart Quiz"):
        restart_quiz()

    st.markdown('</div>', unsafe_allow_html=True)