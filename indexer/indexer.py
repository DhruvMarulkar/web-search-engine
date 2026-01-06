import json
from elasticsearch import Elasticsearch

ES_URL = "http://localhost:9200/"
INDEX_NAME = "pages"

es = Elasticsearch(ES_URL)

#create index if not there
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)
    print("Index created")

#load crawler data
with open("data/pages.json", encoding="utf-8") as f:
    pages = json.load(f)

#index documents
for i, page in enumerate(pages):
    es.index(
        index=INDEX_NAME,
        id=i,
        document={
            "url": page["url"],
            "title": page["title"],
            "content": page["content"]
        }
    )

print(f"Indexed {len(pages)} pages")
