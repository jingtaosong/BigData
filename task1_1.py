import streamlit as st


# page_config
st.set_page_config(page_title="Malaysian Food Quiz", layout="wide")
st.markdown("<h1 style='text-align:center;'>🍛 Malaysian Food Quiz</h1>", unsafe_allow_html=True)
st.divider()

# load_questions
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

with st.container(border=True):
    for question_data in load_questions():
        st.markdown(f"### Q{question_data['id']}. {question_data['question']} (using Type{question_data['type']})")

        # Type B Question with Image
        if question_data["type"].upper() == "B" and question_data["po"]:
            st.image(question_data["po"], width=350)

        for option in question_data["options"]:
            if option.split('.')[0].upper() == question_data["answer"].upper():
                st.markdown(f"<mark><b>{option}</b></mark>", unsafe_allow_html=True)
            else:
                st.write(f"{option}")
