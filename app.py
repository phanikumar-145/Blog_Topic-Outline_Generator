import os
import streamlit as st
from groq import Groq
from langfuse import Langfuse

# ==========================================
# 1. PAGE CONFIGURATION & THEME FIX
# ==========================================
st.set_page_config(
    page_title="Blog Outline Generator",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Blog Outline Generator")
st.write("Generate structured, production-ready blog outlines powered by Groq & Langfuse.")

# ==========================================
# 2. INITIALIZE CLIENTS (READING SECRETS)
# ==========================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Validate Groq credentials gracefully
if not GROQ_API_KEY:
    st.error("❌ `GROQ_API_KEY` is missing! Please add it to your Space Secrets in the Settings tab.")
    st.stop()

# Initialize Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Universal Langfuse Client
if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST
        )
    except Exception:
        langfuse = None
else:
    langfuse = None
    st.warning("⚠️ Langfuse keys not fully configured. App will run without analytics tracking.")

# ==========================================
# 3. GENERATION LOGIC FUNCTION
# ==========================================
def generate_outline(topic, target_audience):
    """Generates a structured outline using Groq LLM and tracks it via Langfuse universally."""
    
    system_prompt = "You are an expert content strategist and SEO specialist."
    user_prompt = f"""Create a detailed, comprehensive blog outline for the topic: '{topic}'.
    Target Audience: {target_audience}
    
    Structure the response explicitly using 'Section 1: [Title]', 'Section 2: [Title]', etc., followed by bullet points detailing what to cover in that section."""

    # Universal tracing structure compatible with all SDK versions
    generation = None
    if langfuse:
        try:
            generation = langfuse.generation(
                name="blog_outline_generation",
                model="llama-3.1-8b-instant",
                input=user_prompt
            )
        except Exception:
            pass

    try:
        # Call Groq API using the updated production model string
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        
        output_text = completion.choices[0].message.content
        
        # Log successful execution output back to Langfuse
        if generation:
            try:
                generation.update(output=output_text)
            except Exception:
                pass
                
        return output_text

    except Exception as e:
        st.error(f"API Error occurred: {e}")
        if generation:
            try:
                generation.update(output=f"Error: {str(e)}")
            except Exception:
                pass
        return None

# ==========================================
# 4. STREAMLIT USER INTERFACE (UI)
# ==========================================
with st.form("outline_form"):
    topic = st.text_input("What is the topic of your blog?", placeholder="e.g., Impact of AI in modern education")
    audience = st.text_input("Target Audience", value="General Public", placeholder="e.g., Teachers, Tech Enthusiasts")
        
    submit_button = st.form_submit_button(label="Generate Outline")

# Execution and Render Output
if submit_button:
    if not topic.strip():
        st.warning("Please enter a valid topic before generating!")
    else:
        with st.spinner("Analyzing data and generating outline..."):
            raw_result = generate_outline(topic, audience)
            
            if raw_result:
                st.success("✨ Your Blog Outline is Ready!")
                st.markdown("---")
                
                # Split raw result into structured UI block components
                sections = raw_result.split("Section ")
                
                if len(sections) > 1:
                    if sections[0].strip():
                        st.write(sections[0].strip())
                        
                    for section in sections[1:]:
                        lines = section.split("\n", 1)
                        header = f"Section {lines[0].strip()}"
                        body = lines[1].strip() if len(lines) > 1 else ""
                        
                        # Native container auto-inverts text color based on light/dark mode
                        with st.container(border=True):
                            st.subheader(header)
                            st.markdown(body)
                else:
                    with st.container(border=True):
                        st.markdown(raw_result)