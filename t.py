import os

def save_to_local():
    DOCUMENTS_PATH = "/home/warden/rag/documen"
    os.makedirs(DOCUMENTS_PATH, exist_ok=True)

save_to_local()