# OUTPUT PARSER FILE

from langchain_core.output_parsers import PydanticOutputParser
from models import Blog

parser = PydanticOutputParser(
    pydantic_object=Blog
)
format_instructions = parser.get_format_instructions()