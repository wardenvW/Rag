from pipeline import Pipeline
from chunker import RecursiveSplitter
from embed import Embedder
from db import VectorStorage
from sentence_transformers import SentenceTransformer
import pathlib
from google import genai
from google.genai import types
import time
import os
from dotenv import load_dotenv


#model = SentenceTransformer("BAAI/bge-m3")
#model.save("./model")

#print(model.get_embedding_dimension())

load_dotenv()

path = pathlib.Path("/home/warden/rag/test6-images.pdf")

API_KEY = os.getenv("API_KEY")
print(API_KEY)
client = genai.Client(api_key=API_KEY)


time_start = time.time()


embedder = Embedder()
db = VectorStorage(collection_name="docs")
print(db.client.get_collection("docs"))


#ppl = Pipeline(chunker=RecursiveSplitter(chunk_size=400), embedder=embedder, vector_db=db)
#ppl.process(["/home/warden/rag/juk.pdf"])

print("DOCS IN DB:", db.client.count("docs"))
def start():
    query = "?"
    query_vector = embedder.embed([query])[0]
    print(len(query_vector))

    results = db.search(query_vector)

    context = "\n\n".join(
    f"[{m.source} | Возможные страницы: {m.page}]\n{text}"
    for m, text in zip(results.meta, results.text)
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
            Отвечай только по предоставленному контексту.
            Если ответа в контексте нет — скажи об этом.
            Указывай все возможные страницы, где упоминается контекст.
            """,
            temperature=0.1,
            max_output_tokens=50000,
        )
    )



    print(response.text)
    print(f"Ответ дан за {(time.time() - time_start):.2f} секунд")

start()
db.close()