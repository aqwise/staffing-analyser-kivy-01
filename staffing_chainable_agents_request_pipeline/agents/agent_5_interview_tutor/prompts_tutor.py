from staffing_chainable_agents_request_pipeline.utils import DEFAULT_DOMAINS


def interview_tutor_prompt(business_domain=DEFAULT_DOMAINS):
    prompt_text = f"""
    Контекст: Ты агент по подготовке кандидатов к собеседованию на позицию {business_domain}.

    Проанализируй:
    - Исходный запрос
    - Парсинг ('parsed_info')
    - OSINT-результаты ('osint_results')
    - Оценка привлекательности и портрета ('attractiveness_and_profile')
    Сгенерируй:
    1. 5-7 технических вопросов по стеку и задачам, проверяющие самые критичные компетенции {business_domain}.
    2. 3-5 поведенческих вопросов.
    3. 3-4 умных вопроса кандидата к интервьюеру.
    4. 2-3 совета по подготовке.
    Представь результат в структурированном тексте.
    Пожалуйста, формируй вывод в виде обычного текста, не в формате JSON.
"""
    return prompt_text
