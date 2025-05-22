from google.adk.agents import Agent
from .prompts import report_finalizer_prompt
from google.adk.tools import google_search 


root_agent = Agent(
    name="report_finalizer_agent",
    model="gemini-2.5-pro-preview-05-06",
    description="Агент для финальной сборки структурированного отчета без изменений содержания.",
    instruction=report_finalizer_prompt(),
)
