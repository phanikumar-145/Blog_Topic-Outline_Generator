import os
import re
import socket
import traceback

import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from prompts import prompt
from parser import parser


# Load environment variables
load_dotenv()


# Page configuration
st.set_page_config(
    page_title="AI Blog Outline Generator",
    page_icon="📝",
    layout="wide"
)


# Check cloud configuration
api_key = os.getenv("GROQ_API_KEY")

st.write(
    "Groq API key configured:",
    bool(api_key)
)

try:
    socket.getaddrinfo("api.groq.com", 443)
    st.write("Groq DNS lookup: successful")
except Exception as e:
    st.write("Groq DNS lookup failed:", str(e))


# Custom styling
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


# Topic validation
def is_valid_topic(topic):
    if not topic or len(topic.strip()) < 2:
        return False

    topic = topic.strip()

    if not re.search(r"[a-zA-Z]", topic):
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
    '<div class="sub-title">'
    'Generate Professional Blog Outlines Instantly'
    '</div>',
    unsafe_allow_html=True
)


# Input fields
col1, col2 = st.columns(2)

with col1:
    topic = st.text_input(
        "📌 Blog Topic",
        placeholder="Artificial Intelligence",
        key="blog_topic"
    )

with col2:
    audience = st.text_input(
        "🎯 Target Audience",
        placeholder="Students",
        key="blog_audience"
    )


# Generate button
generate = st.button(
    "🚀 Generate Outline",
    use_container_width=True,
    key="generate_outline"
)


# Generate blog outline
if generate:

    if not is_valid_topic(topic):
        st.error(
            "Invalid topic provided. "
            "Please enter a meaningful blog topic."
        )

    elif not api_key:
        st.error(
            "GROQ_API_KEY is missing. Add it under "
            "Hugging Face Space Settings → Variables and secrets."
        )

    else:
        try:
            with st.spinner("Generating outline..."):

                llm = ChatGroq(
                    model="openai/gpt-oss-120b",
                    temperature=0,
                    api_key=api_key,
                    timeout=60,
                    max_retries=1
                )

                chain = prompt | llm | parser

                response = chain.invoke({
                    "topic": topic.strip(),
                    "audience": (
                        audience.strip()
                        if audience.strip()
                        else "General Audience"
                    )
                })

            st.success("Outline Generated Successfully!")

            # Blog title
            st.markdown("## 📝 Blog Title")
            st.markdown(
                '<div class="blog-card">',
                unsafe_allow_html=True
            )
            st.subheader(response.blog_title)
            st.markdown("</div>", unsafe_allow_html=True)

            # Outline sections
            st.markdown("## 📚 Outline Sections")

            for i, section in enumerate(
                response.outline_sections,
                start=1
            ):
                st.markdown(f"### Section {i}")
                st.write(section)

            # Audience and writing goal
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🎯 Target Audience")
                st.info(response.target_audience)

            with col2:
                st.markdown("### 🚀 Writing Goal")
                st.success(response.writing_goal)

        except Exception as e:
            st.error(f"Error type: {type(e).__name__}")
            st.code(str(e))

            print("FULL TRACEBACK:")
            traceback.print_exc()

            cause = getattr(e, "__cause__", None)

            if cause:
                print("UNDERLYING CAUSE:", repr(cause))