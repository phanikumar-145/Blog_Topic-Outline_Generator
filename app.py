import os
import streamlit as st
from groq import Groq
from langfuse import Langfuse
from langfuse.openai import openai # Langfuse wrapper for tracking

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
# Hugging Face Spaces automatically inject Settings -> Variables/Secrets into os.environ
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Validate credentials gracefully
if not GROQ_API_KEY:
    st.error("❌ `GROQ_API_KEY` is missing! Please add it to your Space Secrets in the Settings tab.")
    st.stop()

# Initialize Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Langfuse Client if keys are provided
if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )
else:
    langfuse = None
    st.warning("⚠️ Langfuse keys not fully configured. App will run without analytics tracking.")

# ==========================================
# 3. GENERATION LOGIC FUNCTION
# ==========================================
def generate_outline(topic, target_audience, tone):
    """Generates a structured outline using Groq LLM and registers a trace in Langfuse."""
    
    system_prompt = "You are an expert content strategist and SEO specialist."
    user_prompt = f"""Create a detailed, comprehensive blog outline for the topic: '{topic}'.
    Target Audience: {target_audience}
    Tone of Voice: {tone}
    
    Structure the response explicitly using 'Section 1: [Title]', 'Section 2: [Title]', etc., followed by bullet points detailing what to cover in that section."""

    # Trigger Langfuse tracking trace manually if initialized
    trace_id = None
    if langfuse:
        trace = langfuse.trace(name="blog_outline_generation", input={"topic": topic, "tone": tone})
        trace_id = trace.id

    try:
        # Call Groq API using standard Llama-3 model
        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        
        output_text = completion.choices[0].message.content
        
        # Update Langfuse trace with success status
        if langfuse and trace_id:
            langfuse.generation(
                trace_id=trace_id,
                name="llama3_generation",
                model="llama3-8b-8192",
                input=user_prompt,
                output=output_text
            )
            
        return output_text

    except Exception as e:
        if langfuse and trace_id:
            langfuse.trace(id=trace_id, output=f"Error: {str(e)}")
        st.error(f"API Error occurred: {e}")
        return None

# ==========================================
# 4. STREAMLIT USER INTERFACE (UI)
# ==========================================
# Input Form Components
with st.form("outline_form"):
    topic = st.text_input("What is the topic of your blog?", placeholder="e.g., Impact of AI in modern education")
    
    col1, col2 = st.columns(2)
    with col1:
        audience = st.text_input("Target Audience", value="General Public", placeholder="e.g., Teachers, Tech Enthusiasts")
    with col2:
        tone = st.selectbox("Tone of Voice", ["Professional", "Casual", "Informative", "Inspirational", "Witty"])
        
    submit_button = st.form_submit_button(label="Generate Outline")

# Execution and Render Output
if submit_button:
    if not topic.strip():
        st.warning("Please enter a valid topic before generating!")
    else:
        with st.spinner("Analyzing data and generating outline..."):
            raw_result = generate_outline(topic, audience, tone)
            
            if raw_result:
                st.success("✨ Your Blog Outline is Ready!")
                st.markdown("---")
                
                # Parsing blocks to render inside native dynamic boxes
                # This explicitly avoids the dark-on-dark text rendering bug
                sections = raw_result.split("Section ")
                
                # If it split correctly into sections, render them beautifully
                if len(sections) > 1:
                    # Render introductory text if any exists before 'Section 1'
                    if sections[0].strip():
                        st.write(sections[0].strip())
                        
                    for section in sections[1:]:
                        # Parse section sequence number and content body safely
                        lines = section.split("\n", 1)
                        header = f"Section {lines[0].strip()}"
                        body = lines[1].strip() if len(lines) > 1 else ""
                        
                        # Native Streamlit border container that dynamically flips text colors
                        with st.container(border=True):
                            st.subheader(header)
                            st.markdown(body)
                else:
                    # Fallback default text container if layout isn't cleanly structured
                    with st.container(border=True):
                        st.markdown(raw_result)