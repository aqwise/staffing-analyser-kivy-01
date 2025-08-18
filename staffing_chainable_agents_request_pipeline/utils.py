ALLOWED_DOMAINS = ["QA", "AQA", "DevOps"]


def validate_business_domain(business_domain):
    if business_domain in ALLOWED_DOMAINS:
        return business_domain
    else:
        return "QA/AQA"
