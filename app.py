import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Blog Outline Generator",
    page_icon="📝",
    layout="centered"
)

st.title("📝 AI Blog Outline Generator")
st.write("Generate professional blog outlines instantly.")

# -----------------------------
# Load Groq API Key
# -----------------------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    st.error(
        "GROQ_API_KEY is missing. Add it in "
        "Hugging Face Space Settings → Variables and secrets."
    )
    st.stop()

# -----------------------------
# Initialize Groq Model
# -----------------------------
try:
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=GROQ_API_KEY,
        temperature=0.7,
        max_tokens=2000,
        timeout=60,
        max_retries=2
    )
except Exception as e:
    st.error("Could not initialize the Groq model.")
    st.code(f"{type(e).__name__}: {e}")
    st.stop()

# -----------------------------
# Create Prompt Template
# -----------------------------
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert blog writer and SEO content strategist. "
        "Create clear, structured, useful blog outlines."
    ),
    (
        "human",
        """
Create a detailed blog outline for this topic:

Topic: {topic}
Target Audience: {audience}

Requirements:
1. Suggest an engaging, SEO-friendly blog title.
2. Include a short introduction.
3. Organize the outline into numbered sections.
4. Use headings and bullet points.
5. Explain what each section should cover.
6. Include relevant examples where appropriate.
7. Add a conclusion.
8. Suggest relevant SEO keywords at the end.
9. Keep the outline clear and easy to follow.
"""
    )
])

# -----------------------------
# Build LangChain
# -----------------------------
chain = prompt | llm | StrOutputParser()

# -----------------------------
# User Input Form
# -----------------------------
with st.form("blog_outline_form"):
    topic = st.text_input(
        "Blog Topic",
        placeholder="e.g., Impact of AI in modern education"
    )

    audience = st.text_input(
        "Target Audience",
        value="General Public",
        placeholder="e.g., Students, Teachers, Developers"
    )

    submitted = st.form_submit_button(
        "Generate Blog Outline",
        use_container_width=True
    )

# -----------------------------
# Generate Outline
# -----------------------------
if submitted:
    if not topic.strip():
        st.warning("Please enter a blog topic.")

    elif not audience.strip():
        st.warning("Please enter a target audience.")

    else:
        try:
            with st.spinner("Generating your blog outline..."):
                response = chain.invoke({
                    "topic": topic.strip(),
                    "audience": audience.strip()
                })

            st.success("Your blog outline is ready!")
            st.markdown("---")
            st.markdown(response)

            st.download_button(
                label="Download Outline",
                data=response,
                file_name="blog_outline.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error("Failed to generate the blog outline.")

            # Show the error without exposing the API key
            st.write("Error type:")
            st.code(type(e).__name__)

            error_message = str(e).replace(
                GROQ_API_KEY, "[REDACTED]"
            )
            st.write("Error details:")
            st.code(error_message)

            st.info(
                "Check your Groq API key, Hugging Face Space "
                "secrets, and application logs."
            )