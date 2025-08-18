from google.adk.agents import Agent
from staffing_chainable_agents_request_pipeline.agents.agent_4_attractiveness_profiler.prompts_profiler import \
    attractiveness_profiler_prompt


class ParametrizedAttractivenessProfilerAgent(Agent):
    def __init__(self, business_domain=None, **kwargs):
        instruction = attractiveness_profiler_prompt(business_domain)
        super().__init__(instruction=instruction, **kwargs)
        self._business_domain = business_domain
