from google.adk.agents import Agent

from staffing_chainable_agents_request_pipeline.agents.agent_3_osint_researcher.prompts_osint import \
    osint_researcher_prompt


class ParametrizedOSINTAgent(Agent):
    def __init__(self, business_domain=None, **kwargs):
        instruction = osint_researcher_prompt(business_domain)
        super().__init__(instruction=instruction, **kwargs)
        self._business_domain = business_domain
