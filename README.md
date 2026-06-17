# RAGwv — Advanced Hybrid RAG System

## 🛠 Tech stack

* **Backend:** FastAPI, Python 3.12
* **Vector DB:** Qdrant (Hybrid Search: Dense + Sparse)
* **Embeddings & LLM:** Local Deployments (BGE-M3, Русский/English support)
* **Frontend:** React, Tailwind CSS, Lucide Icons, React Router

---

## 🗺 Roadmap (potential ideas)
* [ X ] **Conversation memory (+button on/off)**
* [ X ] **Different documents hadlers ✘ (docling universal) (virtual + python generation for csv)**
* [ X ] **Local LLM integration into MAIN PIPELINE**
* [ X ] **Frontend features**
* [ ✘ ] **New experimental prompt builder:**
```xml
<context>
    <document index="1" type="legal">
        Текст договора...
    </document>
    <document index="2" type="tech">
        Техническая спецификация...
    </document>
</context>
```
