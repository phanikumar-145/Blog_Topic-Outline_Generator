# Streamlit for frontend UI

import streamlit as st

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# LANGCHAIN + GROQ IMPORTS

from langchain_groq import ChatGroq

# Prompt Template
from prompts import prompt

# Output Parser
from parser import parser

# STREAMLIT PAGE CONFIG
st.set_page_config(
    page_title="AI Blog Outline Generator",
    page_icon="📝",
    layout="centered"
)

# APP TITLE

st.title("📝 AI Blog Outline Generator")

# USER INPUTS

# Blog Topic Input
topic = st.text_input(
    "Enter Blog Topic"
)

# Audience Input
audience = st.text_input(
    "Enter Target Audience"
)

if st.button("Generate"):

    # Validate Topic
    if topic:
        # LLM MODEL
        # GROQ + LLAMA MODEL

        llm = ChatGroq(

            # AI MODEL
            model="llama-3.3-70b-versatile",

            # API KEY
            api_key=os.getenv("GROQ_API_KEY")
        )

        # LANGCHAIN CHAIN
        # Prompt → LLM → Parser

        chain = prompt | llm | parser

        # INVOKE CHAIN

        response = chain.invoke({

            # Dynamic Variables
            "topic": topic,

            # Audience input
            "audience": audience
            if audience
            else "General Audience"
        })

        # JSON OUTPUT
        st.subheader("Generated JSON Output")

        st.json(
            response.model_dump()
        )

        # NORMAL OUTPUT

        st.subheader("Blog Title")

        st.write(
            response.blog_title
        )

        st.subheader("Outline Sections")

        for section in response.outline_sections:

            st.write("•", section)


        st.subheader("Target Audience")

        st.write(
            response.target_audience
        )


        st.subheader("Writing Goal")

        st.write(
            response.writing_goal
        )

    # WARNING
    else:

        st.warning(
            "Please enter a blog topic"
        )