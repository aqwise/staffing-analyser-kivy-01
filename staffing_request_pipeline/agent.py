# -*- coding: utf-8 -*-
from google.adk.tools import google_search  # Импортируем инструмент поиска Google
from google.adk.agents.sequential_agent import SequentialAgent
from .sub_agents import customer_identifier_agent
from .sub_agents import request_parser_agent
from .sub_agents import osint_researcher_agent
from .sub_agents import attractiveness_profiler_agent
from .sub_agents import interview_tutor_agent
from .sub_agents import report_finalizer_agent


# --- Root Агент ---
root_agent = SequentialAgent(
    name="staffing_request_pipeline",
    description="Оркестратор для полного анализа стаффинг-запроса на русском языке в текстовом формате.",
    sub_agents=[
        customer_identifier_agent,
        request_parser_agent,
        osint_researcher_agent,
        attractiveness_profiler_agent,
        interview_tutor_agent,
        report_finalizer_agent
    ]
)
