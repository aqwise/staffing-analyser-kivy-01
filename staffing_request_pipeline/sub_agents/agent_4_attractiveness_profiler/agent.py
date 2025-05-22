from google.adk.agents import Agent, LoopAgent
from .prompts import attractiveness_profiler_prompt
from google.adk.tools import google_search 


root_agent = Agent(
    name="attractiveness_profiler_agent",
    model="gemini-2.5-pro-preview-05-06",
    description="Агент для оценки привлекательности вакансии для QA/AQA и построения специфического профиля кандидата на основе возможностей Innowise QA Automation Services.",
    instruction=attractiveness_profiler_prompt(),
    tools=[google_search],
    output_key="attractiveness_profiler_output",
)


# root_agent = LoopAgent(
#     name="osint_researcher_looping_agent",
#     max_iterations=3,
#     sub_agents=[attractiveness_profiler_agent],
#     description="Агент для оценки привлекательности вакансии для QA/AQA и построения специфического профиля кандидата на основе возможностей Innowise QA Automation Services. в цикле.",
#     )
