from rag_wv import Pipeline, RecursiveSplitter, Embedder, VectorStorage, init_logging
from google import genai
from google.genai import types
import time
import os
from dotenv import load_dotenv

load_dotenv()
init_logging()

API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)


time_start = time.time()


embedder = Embedder()
db = VectorStorage() #Починить in_memory=False

start1 = time.time()

ppl = Pipeline(chunker=RecursiveSplitter(), embedder=embedder, vector_db=db)
#ppl.process(["/home/warden/rag/documents/adm-deliktpravoch1.pdf", "/home/warden/rag/documents/КОАП.pdf", "/home/warden/rag/documents/ПИКОАП.pdf"])

def start():
    start_2 = time.time()
    query = """
Что является основной задачей административно-деликтного права
    """
    query_vector = embedder.embed([query])

    results = db.search(query, query_vector["dense"], query_vector["sparse"], debug=True)
    context = "\n\n".join(
    f"[{obj.meta.source} | Возможные страницы: {obj.meta.page}]\n{obj.text}"
    for obj in results
    )

    prompt = f"""
    Контекст:
    {context}

    Ответь в формате:
    Ответ:
    ...
    Источники:
    ... 

    Вопрос:
    {query}
    """

    response = client.models.generate_content(
        model="gemma-4-31b-it",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=f"""
            Ты профессиональный юрист.
            Отвечай по предоставленному контексту и подробно.
            Если ответа в контексте нет — скажи об этом.
            Указывай все возможные страницы, где упоминается контекст.
            Если вопрос стоит общий, то выдавай сразу всю статью и подходящие части.
            Давай структурные ответы (не ставь лишние знаки '*' и так далее).
            Если будет какие-то неточности или несостыковки влияющие на ответ, скажи об этом.
            """,
            temperature=0.5,
        )
    )



    print(response.text)
    print(f"Ответ дан за {(time.time() - time_start):.2f} секунд")
    print(f"LLM работала {(time.time() - start_2):.2f}")
print(f"Сохранил за {(time.time() - start1):.2f}")
start()

db.close()

