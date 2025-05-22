def load_example_markdown(self):
    """Загружает пример markdown текста для тестирования."""
    example_text = """**Итоговый Отчёт по Вакансии Автотестировщик мобильных и веб приложений/Senior**

**1. Общая информация о запросе на вакансию**

*   **Внутренние идентификаторы и ссылки Salesforce:**
    *   CV - QA - - Московская Биржа - atest - R-10973 (Ссылка: https://innowisegroup2.my.salesforce.com/lightning/r/RequestPosition__c/a05J300000WM8GyIAL/view)
    *   CV - Московская Биржа - atest - RU - QA - 020128 (Ссылка: https://innowisegroup2.my.salesforce.com/lightning/r/Opportunity/006J3000005pDH5IAM/view)
*   **Код запроса от Заказчика:** МБ-СПЦ-2025-4944/1 от 22.05.2025 8:57:42 на ИТ-ресурсы для ПАО Московская Биржа.
*   **Компания-посредник:** Innowise Group.
*   **Сейлс менеджер:** Andrey Testov.
*   **Статус проекта:** New.
*   **Сроки:**
    *   Дата окончания подачи заявок: 27.05.2025 09:00.
    *   Срок отправки заказчику: 2025-05-23.
*   **Ограничения:** На запрос можно подать максимум 3 кандидата.
*   **Указания по оформлению:**
    *   ФИО кандидатов указываем полностью.
    *   Чек-лист — это таблица с требованиями из запроса, в которой напротив каждого требования отмечается «да» или «нет» в зависимости от соответствия.
    *   Заполнение информации о кандидате строго по ШАБЛОНУ: [https://docs.google.com/document/d/1zqwT7lV9F8Hr_ZnIdb5iXyMa8dgg5rH7/edit?usp=sharing&ouid=110197969084316916889&rtpof=true&sd=true](https://docs.google.com/document/d/1zqwT7lV9F8Hr_ZnIdb5iXyMa8dgg5rH7/edit?usp=sharing&ouid=110197969084316916889&rtpof=true&sd=true)

--------------------------------------------------

**2. Информация о Заказчике**

*   **Наименование Заказчика:** ПАО «Московская Биржа».
*   **Индустрия проекта:** FinTech.
*   **Описание компании "Московская Биржа":**
    *   **Официальный сайт:** https://www.moex.com/
    *   **Аффилированные ресурсы:**
        *   https://www.nsd.ru/ (НКО АО «Национальный расчетный депозитарий»)
        *   https://www.nationalclearingcentre.ru/ (НКО НКЦ «Национальный Клиринговый Центр» (АО))
        *   https://finuslugi.ru/ (Финуслуги)
        *   https://career.moex.com/ (Карьерный сайт)
        *   https://www.facebook.com/MSKExchange
        *   https://vk.com/moscowexchange
        *   https://vk.com/moex_career
        *   https://habr.com/ru/companies/moex/blog/
        *   https://hh.ru/employer/1336
        *   https://www.youtube.com/@MoscowExchange
        *   https://t.me/moscow_exchange_official
        *   https://dzen.ru/moex_official
    *   **Сфера деятельности:** Крупнейший российский биржевой холдинг, организатор торгов акциями, облигациями, производными инструментами, валютой, инструментами денежного рынка, драгоценными металлами, зерном и сахаром. Оказывает клиринговые, расчетно-депозитарные и информационные услуги.
    *   **Тип компании:** Публичное акционерное общество (ПАО), биржевой холдинг.
    *   **Интересные факты:**"""
    
    self.ids.input_text.text = example_text
    self._update_analyze_button()
