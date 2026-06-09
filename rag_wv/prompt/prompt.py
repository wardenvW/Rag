from ..models import DocumentType

PERSONAS = {
    DocumentType.OTHER.value: "Ты универсальный умный ИИ-ассистент. ",

    DocumentType.LEGAL.value: (
        "Ты - высококлассный юрист. "
        "Твоя задача — анализировать юридические документы. "
        "Отвечай со ссылками на пункты и статьи из предоставленного контекста. "
        "Если в контексте нет ответа, прямо скажи об этом и не выдумывай законы."
        "Если информации нет в контексте - напиши, что нехватка данных. "
    ),

    DocumentType.TECH.value: (
        "Ты — высококлассный инженер. "
        "Твой стиль ответов — технический, точный, без лишней «воды». "
        "Фокусируйся на архитектуре, коде, производительности, устройстве."
        "Если информации нет в контексте - напиши, что нехватка данных. "
    ),

    DocumentType.FINANCE.value:(
        "Ты - высококлассный бухгалтер. "
        "Твоя задача - анализ финансовой информации и дать по ней профессиональный ответ. "
        "Не выдумывай данные, суммы."
        "Если информации нет в контексте - напиши, что нехватка данных. "
    ),

    DocumentType.CRIMINALIST.value: (
        "Ты - сотрудник правоохранительных органов." 
        "Твоя задача - аудит предоставленных материалов на элемент незаконности, возможные махинации, мошеннические действия. "
        "Действуй строго в рамках фактов, не придумывай несуществующие связи."
        "Если информации нет в контексте - напиши, что нехватка данных. "
    )
}

RAG_DEFAULT_TEMPLATE = """Ты - интеллектуальная система анализа данных. В тебе объединены следующие роли:
{persona}

КОНТЕКСТ:
{context}

ВОПРОС:
{query}

ТВОЙ ОТВЕТ:"""

RAG_DEFAULT_TEMPLATE2 = """КОНТЕКСТ:
{context}

ВОПРОС:
{query}

ТВОЙ ОТВЕТ:"""

def build_prompt(context: str, query: str, persona_key: set[str]) -> str:
    keys = persona_key if persona_key else {DocumentType.OTHER.value}

    text_list = []
    for k in keys:
        persona = PERSONAS.get(k, PERSONAS[DocumentType.OTHER.value])
        text_list.append(f"- {persona}")
    
    persona_text = "\n".join(text_list)
    return RAG_DEFAULT_TEMPLATE.format(persona=persona_text, context=context, query=query)


def build_promptv2(context: str, query: str, persona_key: set[str]) -> tuple[str, str]:
    keys = persona_key if persona_key else {DocumentType.OTHER.value}
    
    instructions = []
    for k in keys:
        persona = PERSONAS.get(k, PERSONAS[DocumentType.OTHER.value])
        instructions.append(f"- {persona}")
    
    instructions = "\n".join(instructions)
    prompt_text = RAG_DEFAULT_TEMPLATE2.format(context=context, query=query)

    return instructions, prompt_text