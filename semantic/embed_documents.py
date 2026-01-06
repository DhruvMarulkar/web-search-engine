import json
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

ES_URL = "http://localhost:9200"
INDEX_NAME = "pages"

model = SentenceTransformer("all-MiniLM-L6-v2")
es = Elasticsearch(ES_URL, verify_certs=False)

with open("data/pages.json", encoding="utf-8") as f:
    pages = json.load(f)

print("Generating embeddings...")

for i, page in enumerate(pages):
    title = page.get("title", "")
    content = page.get("content", "")
    text = title + " " + content

    embedding = model.encode(text).tolist()

    es.update(
        index=INDEX_NAME,
        id=i,
        doc={
            "embedding": embedding
        }
    )

print("Embeddings added to Elasticsearch")
