from langchain_core.prompts import ChatPromptTemplate

from parser import format_instructions

# SYSTEM MESSAGE

system_message = """
You are an expert AI Blog Generator.

Generate the following:

1. Blog Title
2. Blog Outline Sections
3. Target Audience
4. Writing Goal

Expected Output Schema:

{{
 "blog_title": "string",
 "outline_sections": ["string"],
 "target_audience": "string",
 "writing_goal": "string"
}}

Instructions:
- Return output only in proper JSON format
- Generate minimum 5 outline sections
- If audience is missing, use General Audience
- Keep the title catchy and professional

{format_instructions}
"""

# HUMAN / USER MESSAGE

user_message = """
TOPIC:
{topic}

AUDIENCE:
{audience}
"""

# CHAT PROMPT TEMPLATE
# Combines: System Message + Human Message

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_message),
        ("human", user_message)
    ]
)

# PARTIAL VARIABLES
# Inject parser instructions dynamically

prompt = prompt.partial(
    format_instructions=format_instructions
)