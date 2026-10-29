
import os
import streamlit as st
import httpx

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
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
# Check API Key
# -----------------------------
if not GROQ_API_KEY:
    st.error(
        "Groq API key is missing. Add GROQ_API_KEY to your "
        "local .env file or Hugging Face Space secrets."
    )
    st.stop()

# -----------------------------
# Test Groq Connection
# -----------------------------
with st.expander("Connection diagnostics"):
    st.write("Groq API key configured: True")

    try:
        response = httpx.get(
            "https://api.groq.com/openai/v1/models",
            timeout=15
        )
        st.write("Groq DNS/HTTPS connection: successful")
        st.write("Groq HTTP status:", response.status_code)

        if response.status_code == 401:
            st.warning(
                "The endpoint is reachable, but this unauthenticated "
                "test does not verify your API key."
            )

    except httpx.TimeoutException:
        st.warning(
            "Connection timed out. Try again and check Groq's status."
        )
    except httpx.RequestError as e:
        st.warning(
            f"Connection test failed: {type(e).__name__}: {e}"
        )

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
    topic = topic.strip()
    audience = audience.strip()

    if len(topic) < 3 or not any(c.isalnum() for c in topic):
        st.warning(
            "Please enter a meaningful blog topic "
            "containing at least 3 characters."
        )

    elif not audience:
        st.warning("Please enter a target audience.")

    else:
        try:
            with st.spinner("Generating your blog outline..."):
                result = chain.invoke({
                    "topic": topic,
                    "audience": audience
                })

            st.success("Your blog outline is ready!")
            st.markdown("---")
            st.markdown(result)

            st.download_button(
                label="Download Outline",
                data=result,
                file_name="blog_outline.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error("Failed to generate the blog outline.")
            st.write("Error type:")
            st.code(type(e).__name__)

            # Avoid showing the API key in error output
            error_message = str(e)
            if GROQ_API_KEY:
                error_message = error_message.replace(
                    GROQ_API_KEY, "[REDACTED]"
                )

            st.write("Error details:")
            st.code(error_message)

            st.info(
                "If the error is a connection error, check the "
                "Groq service status and Hugging Face Space logs. "
                "If it is a model error, verify the model ID in "
                "Groq's supported models documentation."
            )
