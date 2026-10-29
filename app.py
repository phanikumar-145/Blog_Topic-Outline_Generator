
import os
import traceback

import streamlit as st
from groq import Groq
from langfuse import Langfuse

# -----------------------------
# Streamlit page configuration
# -----------------------------
st.set_page_config(
    page_title="Blog Outline Generator",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Blog Outline Generator")
st.write(
    "Generate structured, production-ready blog outlines "
    "powered by Groq and Langfuse."
)

# -----------------------------
# Environment variables
# -----------------------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get(
    "LANGFUSE_HOST",
    "https://cloud.langfuse.com"
)

# -----------------------------
# Check Groq API key
# -----------------------------
if not GROQ_API_KEY:
    st.error(
        "GROQ_API_KEY is missing. "
        "Add it under your Hugging Face Space Settings "
        "in Variables and secrets."
    )
    st.stop()

# -----------------------------
# Initialize Groq client
# -----------------------------
try:
    groq_client = Groq(
        api_key=GROQ_API_KEY,
        timeout=60.0,
        max_retries=2
    )
except Exception as e:
    st.error("Failed to initialize the Groq client.")
    st.code(f"{type(e).__name__}: {e}")
    st.stop()

# -----------------------------
# Initialize Langfuse (optional)
# -----------------------------
langfuse = None

if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST
        )
    except Exception as e:
        st.warning(
            "Langfuse initialization failed. "
            "The app will continue without analytics."
        )
        print("Langfuse initialization error:")
        print(traceback.format_exc())
else:
    st.info(
        "Langfuse keys are not configured. "
        "The app will run without analytics tracking."
    )


# -----------------------------
# Generate blog outline
# -----------------------------
def generate_outline(topic, target_audience):

    system_prompt = (
        "You are an expert content strategist and SEO specialist. "
        "Create clear, useful, well-organized blog outlines."
    )

    user_prompt = f"""
Create a detailed blog outline for the topic: "{topic}".

Target Audience: {target_audience}

Requirements:
1. Create a suitable blog title.
2. Organize the outline into numbered sections.
3. Use the format "Section 1: [Title]".
4. Include bullet points explaining what each section should cover.
5. Include a conclusion.
6. Make the outline useful for the specified target audience.
"""

    generation = None

    # Optional Langfuse tracing
    if langfuse:
        try:
            generation = langfuse.generation(
                name="blog_outline_generation",
                model="llama-3.1-8b-instant",
                input=user_prompt
            )
        except Exception:
            print("Langfuse tracing initialization failed:")
            print(traceback.format_exc())

    try:
        # Call Groq API
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.7,
            max_tokens=2500
        )

        output_text = completion.choices[0].message.content

        if not output_text:
            raise ValueError("Groq returned an empty response.")

        # Record successful generation
        if generation:
            try:
                generation.update(output=output_text)
            except Exception:
                print("Langfuse output tracking failed:")
                print(traceback.format_exc())

        return output_text

    except Exception as e:
        # Print full details in Hugging Face Space Logs
        print("GROQ API ERROR")
        print(traceback.format_exc())

        # Show diagnostic details in the app
        st.error("The request to the Groq API failed.")
        st.write("Error type:")
        st.code(type(e).__name__)

        st.write("Error details:")
        st.code(str(e))

        cause = e.__cause__ or e.__context__

        if cause:
            st.write("Underlying cause:")
            st.code(f"{type(cause).__name__}: {cause}")

        # Record failure without hiding the original error
        if generation:
            try:
                generation.update(
                    output="Generation failed"
                )
            except Exception:
                print("Langfuse error tracking failed:")
                print(traceback.format_exc())

        return None


# -----------------------------
# User interface
# -----------------------------
with st.form("outline_form"):

    topic = st.text_input(
        "What is the topic of your blog?",
        placeholder="e.g., Impact of AI in modern education"
    )

    audience = st.text_input(
        "Target Audience",
        value="General Public",
        placeholder="e.g., Teachers, Tech Enthusiasts"
    )

    submit_button = st.form_submit_button(
        label="Generate Outline"
    )


# -----------------------------
# Display results
# -----------------------------
if submit_button:

    if not topic.strip():
        st.warning("Please enter a valid blog topic.")

    elif not audience.strip():
        st.warning("Please enter a target audience.")

    else:
        with st.spinner("Generating your blog outline..."):
            raw_result = generate_outline(
                topic.strip(),
                audience.strip()
            )

        if raw_result:
            st.success("✨ Your Blog Outline is Ready!")
            st.markdown("---")

            clean_result = raw_result.replace("**", "")

            # Separate appendix, if present
            appendix_content = None

            if "Appendix:" in clean_result:
                main_outline, appendix_content = (
                    clean_result.split("Appendix:", 1)
                )
            elif "Appendix" in clean_result:
                main_outline, appendix_content = (
                    clean_result.split("Appendix", 1)
                )
            else:
                main_outline = clean_result

            # Display sections
            sections = main_outline.split("Section ")

            if len(sections) > 1:

                if sections[0].strip():
                    st.markdown(sections[0].strip())

                for section in sections[1:]:
                    lines = section.split("\n", 1)

                    header = f"Section {lines[0].strip()}"

                    body = (
                        lines[1].strip()
                        if len(lines) > 1
                        else ""
                    )

                    with st.container(border=True):
                        st.subheader(header)
                        st.markdown(body)

            else:
                with st.container(border=True):
                    st.markdown(main_outline.strip())

            # Display appendix
            if appendix_content:
                with st.container(border=True):
                    st.subheader("📚 Appendix & Extras")
                    st.markdown(appendix_content.strip())
