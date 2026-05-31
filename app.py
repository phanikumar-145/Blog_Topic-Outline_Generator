import re
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from prompts import prompt
from parser import parser

load_dotenv()

# -------------------------
# Page Config
# -------------------------

st.set_page_config(
    page_title="AI Blog Outline Generator",
    page_icon="📝",
    layout="wide"
)

# Custom Styling

st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
}

.sub-title {
    text-align: center;
    color: gray;
    margin-bottom: 30px;
}

.blog-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #1E293B;
    margin-bottom: 20px;
}

.section-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #111827;
    margin-bottom: 10px;
    border-left: 5px solid #3B82F6;
}

</style>
""", unsafe_allow_html=True)

# Validation

def is_valid_topic(topic):

    if not topic:
        return False

    topic = topic.strip()

    if len(topic) < 2:
        return False

    if re.fullmatch(r"\d+", topic):
        return False

    if re.fullmatch(r"[^\w\s]+", topic):
        return False

    return True

# Header

st.markdown(
    '<div class="main-title">📝 AI Blog Outline Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Generate Professional Blog Outlines Instantly</div>',
    unsafe_allow_html=True
)

# Inputs

col1, col2 = st.columns(2)

with col1:
    topic = st.text_input(
        "📌 Blog Topic",
        placeholder="Artificial Intelligence"
    )

with col2:
    audience = st.text_input(
        "🎯 Target Audience",
        placeholder="Students"
    )

generate = st.button(
    "🚀 Generate Outline",
    use_container_width=True
)

# -------------------------
# LLM
# -------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

chain = prompt | llm | parser

# -------------------------
# Generate
# -------------------------

if generate:

    if not is_valid_topic(topic):

        st.error(
            "Invalid topic provided. Please enter a meaningful blog topic."
        )

    else:

        try:

            with st.spinner("Generating outline..."):

                response = chain.invoke(
                    {
                        "topic": topic,
                        "audience": audience
                    }
                )

            st.success("Outline Generated Successfully!")

            st.markdown("## 📝 Blog Title")

            st.markdown(
                f"""
                <div class="blog-card">
                    <h3>{response.blog_title}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("## 📚 Outline Sections")

            for i, section in enumerate(
                response.outline_sections,
                start=1
            ):

                st.markdown(
                    f"""
                    <div class="section-card">
                        <b>Section {i}</b><br><br>
                        {section}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🎯 Target Audience")
                st.info(response.target_audience)

            with col2:
                st.markdown("### 🚀 Writing Goal")
                st.success(response.writing_goal)

        except Exception as e:

            st.error(f"Error: {e}")