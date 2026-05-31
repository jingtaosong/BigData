from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import os


# Question Bank
@st.cache_data
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
            photo = parts[8] if qtype.upper() == "B" else ""
            questions.append({
                "id": qid,
                "type": qtype,
                "question": q,
                "options": [a, b, c, d],
                "answer": ans,
                "photo": photo
            })
    return questions

# Session State Initialization
def init_session_state():
    """Unify the initialization of session_state to ensure correct default values"""
    default_states = {
        "current_question": 0,
        "answers": [None] * TOTAL_QUESTIONS,
        "quiz_submitted": False,
        "participant_name": "",
        "result_df": None,
        "final_score": None,
        "is_balloons": False
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.dialog("Matrix Details", width="large", dismissible=False)
def show_matrix():
    """Display a matrix"""
    col1, col2 = st.columns([10, 2])
    with col2:
        if st.button("quit", type="primary", use_container_width=True):
            st.rerun()
    st.session_state.is_balloons = False
    load_data.clear()
    df_data_all = load_data("results/quiz_results.csv")
    if len(df_data_all) < 5:
        st.error("Fewer than five participants, so the matrix cannot be displayed")
    else:
        display_matrix(df_data_all)

@st.dialog("Chart Details", width="large", dismissible=False)
def show_chart():
    """Display charts"""
    col1, col2 = st.columns([10, 2])
    with col2:
        if st.button("quit", type="primary", use_container_width=True):
            st.rerun()
    st.session_state.is_balloons = False
    load_data.clear()
    # Read all historical data
    df_data_all = load_data("results/quiz_results.csv")
    if len(df_data_all) < 5:
        st.error("Fewer than five participants, so the charts cannot be displayed")
    else:
        generate_chart(df_data_all)

def crate_result_dataframe(score):
    """Crate the result dataframe. Display results and save to csv file"""
    result_data = {
        "Question": [],
        "Participant Answer": [],
        "Correct Answer": [],
        "Result": []
    }
    row_record = {
        "Date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": st.session_state.participant_name,
    }

    for index, question in enumerate(QUESTIONS):
        participant_answer = st.session_state.answers[index]
        correct_answer = question["answer"]

        if participant_answer == correct_answer:
            result = "Correct"
        else:
            result = "Wrong"

        result_data["Question"].append(f"Question {index + 1}")
        result_data["Participant Answer"].append(participant_answer)
        result_data["Correct Answer"].append(correct_answer)
        result_data["Result"].append(result)

        row_record[f"Q{index + 1}"] = participant_answer

    # Save Results to CSV File
    result_file = "results/quiz_results.csv"
    row_record["Score"] = score
    row_record["Percentage"] = round((score / TOTAL_QUESTIONS) * 100, 2)
    save_dataframe = pd.DataFrame([row_record])
    if os.path.exists(result_file):
        save_dataframe.to_csv(result_file, mode="a", header=False, index=False)
    else:
        save_dataframe.to_csv(result_file, index=False)

    return pd.DataFrame(result_data)

# quiz_result.csv data
@st.cache_data
def load_data(file):
    """read quiz_result.csv data"""
    return pd.read_csv(file)

def display_matrix(df):
    """Generate a matrix"""
    st.subheader("SAMPLE OF QUIZ MATRIX RESULTS：")
    st.markdown(f"No. of elements {df.size}")
    st.markdown(f"No. of records {len(df)}")

    # columns = ["Name"] + [f"Q{i + 1}" for i in range(TOTAL_QUESTIONS)] + ["Score", "Percentage"]
    # df_matrix = df[columns].copy()
    # st.dataframe(df_matrix, use_container_width=True)
    df_cols = df.columns[df.columns != "Date"]
    st.dataframe(df[df_cols], use_container_width=True)

    scores = df["Score"]
    percentages = df["Percentage"]

    col_score, col_percentage = st.columns(2)
    # Score Statistics
    with col_score:
        st.markdown("===================---SCORE===================---")
        st.markdown(f"Mean value for Score: {scores.mean():.2f}")
        st.markdown(f"Median value for Score: {scores.median():.2f}")
        st.markdown(f"Mode value for Score: {scores.mode().iloc[0]}")
        st.markdown(f"Lowest Score: {scores.min()}")
        st.markdown(f"Highest Score: {scores.max()}")

    # Percentage Statistics
    with col_percentage:
        st.markdown("===================PERCENTAGE===================")
        st.markdown(f"Mean value for Percentage: {percentages.mean():.2f}")
        st.markdown(f"Median value for Percentage: {percentages.median():.2f}")
        st.markdown(f"Mode value for Percentage: {percentages.mode().iloc[0]:.2f}")
        st.markdown(f"Lowest Percentage: {percentages.min():.2f}")
        st.markdown(f"Highest Percentage: {percentages.max():.2f}")

def create_chart1(df):
    """Generate participant total score"""
    return alt.Chart(df).mark_bar(
        cornerRadius=6
    ).encode(
        x=alt.X("Name:N", title="Participant", axis=alt.Axis(labelAngle=-75, labelAlign="right")),
        y=alt.Y("Score:Q", title="Score", scale=alt.Scale(domain=[0, TOTAL_QUESTIONS])),
        color=alt.Color("Score:Q", scale=alt.Scale(scheme="viridis"), legend=None),
        tooltip=[alt.Tooltip("Name:N"), alt.Tooltip("Score:Q")]
    ).properties(
        title=alt.Title("Participant Total Scores", align="center", anchor="middle"),
        height=300
    )

def create_chart2(df):
    """Generate participant total score with median line"""
    median_score = df["Score"].median()

    # bar
    bars = alt.Chart(df).mark_bar(
        cornerRadius=6,
        color="#4C78A8"
    ).encode(
        x=alt.X("Name:N", title="Participant", axis=alt.Axis(labelAngle=-75, labelAlign="right")),
        y=alt.Y("Score:Q", title="Score", scale=alt.Scale(domain=[0, TOTAL_QUESTIONS])),
        tooltip=[alt.Tooltip("Participant:N"), alt.Tooltip("Score:Q")]
    ).properties(
        title=alt.Title("Scores & Median", align="center", anchor="middle"),
        height=300
    )

    # Legend
    legend_score = alt.Chart(pd.DataFrame({"cat": ["Score"]})).mark_square(
        color="#4C78A8", size=120
    ).encode(
        color=alt.Color(
            "cat:N",
            scale=alt.Scale(domain=["Score", "Median"], range=["#4C78A8", "red"]),
            legend=alt.Legend(title="Legend", symbolType="square")
        )
    )

    text = alt.Chart(df).mark_text(
        fontSize=14, fontWeight="bold", color="green", dy=-5
    ).encode(x="Name:N", y="Score:Q", text="Score:Q")

    # Median
    median_line = alt.Chart(pd.DataFrame({"Median": [median_score], "cat": ["Median"]})).mark_rule(
        strokeWidth=4, color="red"
    ).encode(
        y="Median:Q",
        color=alt.Color(
            "cat:N",
            scale=alt.Scale(domain=["Score", "Median"], range=["#4C78A8", "red"]),
            legend=alt.Legend(title="Legend", symbolType="stroke")
        )
    )

    median_text = alt.Chart(
        pd.DataFrame({"Median": [median_score], "Label": [f"{median_score:.2f}"]})
    ).mark_text(
        align="left", dx=5, dy=-8, color="red", fontSize=14, fontWeight="bold"
    ).encode(y="Median:Q", text="Label:N")

    chart = bars + text + median_line + median_text

    return chart

def create_chart3(df):
    """Generate average score charts and percentage charts"""
    mean_score = df["Score"].mean()

    x = np.arange(len(df))
    names = df["Name"].values
    percentages = df["Percentage"].values

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Left Y-axis：score
    ax1.set_xlabel("Participant")
    ax1.set_ylabel("Raw Score", color="#d62828", fontsize=12)
    ax1.set_ylim(0, 4)
    ax1.tick_params(axis="y", labelcolor="#d62828")

    mean_line = ax1.axhline(y=mean_score, color="#d62828", linestyle="--", linewidth=3, label="Mean Score")

    # Right Y-axis: smoothed percentage curve
    ax2 = ax1.twinx()
    ax2.set_ylabel("Percentage (%)", color="#E63946", fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.tick_params(axis="y", labelcolor="#E63946")

    # Smooth curve
    x_smooth = np.linspace(x.min(), x.max(), 300)
    y_smooth = np.interp(x_smooth, x, percentages)

    ax2.plot(x_smooth, y_smooth, color="#E63946", linewidth=3, label="Percentage")
    ax2.scatter(x, percentages, color="#E63946", s=80, zorder=5)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    # X-axis
    ax1.set_xticks(x)
    ax1.set_xticklabels(names)
    plt.title("Participant Percentage & Mean Score", fontsize=14, pad=12)
    plt.tight_layout()

    return fig

def create_chart4(df):
    """Generate participant score distribution charts"""
    mean_score = df['Score'].mean()

    # Scatter plot: Each dot represents the score of one participant
    df["Percentage_Label"] = df["Percentage"].round(2).astype(str) + "%"
    scatter = alt.Chart(df).mark_point(
        filled=True,
        size=100,
        color="#4C78A8"
    ).encode(
        x=alt.X("Name:N", title="Participant", axis=alt.Axis(labelAngle=-75, labelAlign="right")),
        y=alt.Y("Score:Q", title="Score", scale=alt.Scale(domain=[0, df['Score'].max() + 0.5])),
        tooltip=[
            alt.Tooltip("Name:N", title="Participant"),
            alt.Tooltip("Score:Q", title="Score"),
            alt.Tooltip("Percentage_Label:N", title="Percentage")
        ]
    )

    # average score
    mean_line = alt.Chart(pd.DataFrame({"Mean": [mean_score]})).mark_rule(
        color="red", strokeWidth=3, strokeDash=[5, 3]
    ).encode(y="Mean:Q")

    mean_text = alt.Chart(pd.DataFrame({
        "Mean": [mean_score],
        "Label": [f"Average Score: {mean_score:.2f}"]
    })).mark_text(
        color="red",
        fontSize=12,
        fontWeight="bold",
        dx=10,
        dy=-10
    ).encode(y="Mean:Q", text="Label:N")

    chart = (scatter + mean_line + mean_text).properties(
        title=alt.Title("Participant Score Distribution", anchor="middle", align="center"),
        height=400,
        width=600
    )

    return chart

def generate_chart(df):
    """Generate 4 charts in 2 x 2 layout"""
    # Chart1:Participant Total Score
    chart1 = create_chart1(df)

    # Chart2:participant total score with median line
    chart2 = create_chart2(df)

    # Chart3:average score charts and percentage charts
    chart3 = create_chart3(df)

    # Chart4:participant score distribution
    chart4 = create_chart4(df)

    # 2 x 2 Layout
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart1, use_container_width=True)
    with col2:
        st.altair_chart(chart2, use_container_width=True)
    col3, col4 = st.columns(2)
    with col3:
        st.pyplot(chart3, use_container_width=True)
    with col4:
        st.altair_chart(chart4, use_container_width=True)


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

QUESTIONS = load_questions()
TOTAL_QUESTIONS = len(QUESTIONS)

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

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Matrix"):
            show_matrix()
    with col2:
        if st.button("View Chart"):
            show_chart()

# Display Current Question
if not st.session_state.quiz_submitted:
    current_index = st.session_state.current_question
    question_data = QUESTIONS[current_index]

    st.subheader(f"Question {current_index + 1} of {TOTAL_QUESTIONS}")

    with st.container(border=True):
        st.markdown(f"### Q{question_data['id']}. {question_data['question']} (using Type{question_data['type']})")

        # Type B Question with Image
        if question_data["type"].upper() == "B" and question_data["photo"]:
            st.image(question_data["photo"], width=350)

        # Restore Previous Answer
        previous_answer = st.session_state.answers[current_index]
        # selected_index = question_data["options"].index(previous_answer) if previous_answer in question_data["options"] else None
        selected_index = None
        for idx, opt in enumerate(question_data["options"]):
            if previous_answer and opt.startswith(previous_answer):
                selected_index = idx
                break

        # Radio Button Options
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
        if st.button("⬅ Previous", disabled=current_index == 0):
            st.session_state.current_question -= 1
            st.rerun()
    with column2:
        if st.button("Next ➡", disabled=current_index == TOTAL_QUESTIONS - 1):
            st.session_state.current_question += 1
            st.rerun()

    # Submit Button
    all_answered = all(answer is not None for answer in st.session_state.answers)
    submit_button = st.button(
        "✅ Submit Quiz",
        use_container_width=True,
        disabled=(not all_answered) or st.session_state.quiz_submitted
    )
else:
    submit_button = False

# Quiz Result Processing
if submit_button:
    # Validate Name
    if not participant_name.strip():
        st.error("Please enter your name.")
        st.stop()

    # Calculate Score
    score = 0
    for user_answer, question in zip(st.session_state.answers, QUESTIONS):
        if user_answer == question["answer"]:
            score += 1

    # Save answer
    with open("answers.txt", "a", encoding="utf-8") as f:
        ans_str = ",".join(st.session_state.answers)
        f.write(f"{datetime.today().strftime(format="%Y-%m-%d %H:%M:%S")}: {participant_name},{score},{ans_str}\n")

    # Create Result DataFrame and Save Results to CSV File
    result_dataframe = crate_result_dataframe(score)
    st.session_state.result_df = result_dataframe
    st.session_state.final_score = score
    st.session_state.quiz_submitted = True
    st.session_state.is_balloons = True
    st.rerun()

if st.session_state.quiz_submitted:
    # Display Result
    st.success(f"🎉 Well done!")
    st.subheader(
        f"{st.session_state.participant_name}, Your Total Score: {st.session_state.final_score}/{TOTAL_QUESTIONS}")
    st.markdown("## 📋 Score Distribution Table：")
    st.dataframe(st.session_state.result_df, use_container_width=True)
    if st.session_state.is_balloons:
        st.balloons()

# Exit Button
if st.session_state.quiz_submitted:
    st.divider()
    if st.button("❌ Exit"):
        st.session_state.clear()
        st.rerun()
