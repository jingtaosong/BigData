import streamlit as st
import os

# Create Required Folders
os.makedirs("results", exist_ok=True)

# Streamlit Page Configuration
st.set_page_config(
    page_title="Malaysian Food Knowledge Quiz",
    page_icon="🍛",
    layout="wide"
)

st.title("🍛 Malaysian Food Knowledge Quiz")
st.markdown("### Discover Malaysian Food and Its Origins")
st.divider()


# Question Bank
def load_questions():
    questions = []
    with open("questions.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            qid = parts[0]
            qtype = parts[1]
            q = parts[2]
            a = parts[3]
            b = parts[4]
            c = parts[5]
            d = parts[6]
            ans = parts[7]
            po = parts[8] if qtype.upper() == "B" else ""
            questions.append({
                "id": qid,
                "type": qtype,
                "question": q,
                "options": [a, b, c, d],
                "answer": ans,
                "po": po
            })
    return questions


questions = load_questions()
TOTAL_QUESTIONS = len(questions)


# Session State Initialization
def init_session_state():
    """统一初始化session_state，确保默认值正确"""
    default_states = {
        "current_question": 0,
        "answers": [None] * TOTAL_QUESTIONS,
        "quiz_submitted": False,
        "participant_name": ""
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Perform initialization
init_session_state()

# Sidebar Participant Information
with st.sidebar:
    st.header("👤 Participant Information")
    participant_name = st.text_input(
        "Enter Your Full Name",
        key="participant_name",
        value=st.session_state.participant_name,
        placeholder="Your Name"
    )
    st.info(f"This quiz contains {TOTAL_QUESTIONS} questions.")

# Display Current Question (仅在未提交时显示题目)
if not st.session_state.quiz_submitted:
    current_index = st.session_state.current_question
    question_data = questions[current_index]

    st.subheader(f"Question {current_index + 1} of {TOTAL_QUESTIONS}")

    with st.container(border=True):
        st.markdown(f"### Q{question_data['id']}. {question_data['question']} (using Type{question_data['type']})")

        # Type B Question with Image
        if question_data["type"].upper() == "B" and question_data["po"]:
            st.image(question_data["po"], width=350)

        # Restore Previous Answer
        previous_answer = st.session_state.answers[current_index]

        if previous_answer in question_data["options"]:
            selected_index = question_data["options"].index(previous_answer)
        else:
            selected_index = None

        # =================================================
        # Radio Button Options
        # =================================================
        selected_answer = st.radio(
            "Choose Your Answer:",
            question_data["options"],
            index=selected_index,
            key=f"question_{current_index}",
            label_visibility="collapsed",
            disabled=st.session_state.quiz_submitted
        )

        if selected_answer:
            st.session_state.answers[current_index] = selected_answer.split(".")[0]

    # Navigation Buttons
    column1, column2, column3 = st.columns([1, 1, 6])

    with column1:
        if st.button(
                "⬅ Previous",
                disabled=current_index == 0
        ):
            st.session_state.current_question -= 1
            st.rerun()

    with column2:
        if st.button(
                "Next ➡",
                disabled=current_index == TOTAL_QUESTIONS - 1
        ):
            st.session_state.current_question += 1
            st.rerun()

    # =====================================================
    # Submit Button
    # =====================================================
    all_answered = all(answer is not None for answer in st.session_state.answers)
    submit_button = st.button(
        "✅ Submit Quiz",
        use_container_width=True,
        disabled=(not all_answered) or st.session_state.quiz_submitted
    )
else:
    submit_button = False  # 提交后隐藏按钮

# =====================================================
# Quiz Result Processing
# =====================================================
if submit_button:
    # ================================================
    # Validate Name
    # ================================================
    if not participant_name.strip():
        st.error("Please enter your name.")
        st.stop()

    # Calculate Score
    score = 0
    for user_answer, question in zip(st.session_state.answers, questions):
        if user_answer == question["answer"]:
            score += 1

    # 显示结果
    st.success(f"🎉 {participant_name}, your score: {score}/{TOTAL_QUESTIONS}")
    st.session_state.quiz_submitted = True
    st.balloons()

# Quit Button
st.divider()
if st.session_state.quiz_submitted and st.button("❌ Quit"):
    st.session_state.clear()

    st.rerun()