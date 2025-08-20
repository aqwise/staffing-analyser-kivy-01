from google.adk.agents import Agent
from staffing_chainable_agents_request_pipeline.agents.agent_6_report_finalizer.prompts_finalizer import \
    report_finalizer_prompt


class ParametrizedReportFinalizerAgent(Agent):
    def __init__(self, business_domain=None, **kwargs):
        instruction = report_finalizer_prompt(business_domain)
        super().__init__(instruction=instruction, **kwargs)
        self._business_domain = business_domain
