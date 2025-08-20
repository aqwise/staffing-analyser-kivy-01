ALLOWED_DOMAINS = ["QA", "AQA", "DevOps"]
DEFAULT_DOMAINS = "QA/AQA"
AI_MODEL = "gemini-2.5-pro-preview-05-06"


def validate_business_domain(business_domain):
    if business_domain in ALLOWED_DOMAINS:
        return business_domain
    else:
        return DEFAULT_DOMAINS
