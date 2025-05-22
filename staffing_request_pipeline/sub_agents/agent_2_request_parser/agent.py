from google.adk.agents import Agent
from .prompts import request_parsing_prompt
from google.adk.tools import google_search 


root_agent = Agent(
    name="request_parser_agent",
    model="gemini-2.5-pro-preview-05-06",
    description="Агент для извлечения ключевой информации из стаффинг-запроса и форматирования в текст.",
    instruction=request_parsing_prompt(),
    tools=[google_search],
    output_key="request_parser_agent_output",
)
