from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



ES_URL = "http://localhost:9200"
INDEX_NAME = "pages"

es = Elasticsearch(ES_URL, verify_certs=False)

model = SentenceTransformer("all-MiniLM-L6-v2")



@app.get("/ping")
def ping():
    return {"status": "backend alive"}



@app.get("/search")
def search(q: str):
    if not q.strip():
        return []

    q = q.strip()
    words = q.split()
    is_single_word = len(words) == 1



    if is_single_word:
        res = es.search(
            index=INDEX_NAME,
            size=10,
            query={
                "multi_match": {
                    "query": q,
                    "fields": ["title^2", "content"],
                    "fuzziness": "AUTO",
                    "prefix_length": 2
                }
            },
            highlight={
                "fields": {
                    "content": {}
                }
            }
        )

    

    
    else:
        query_vector = model.encode(q).tolist()

        res = es.search(
            index=INDEX_NAME,
            size=10,
            query={
                "script_score": {
                    "query": {
                        "multi_match": {
                            "query": q,
                            "fields": ["title^2", "content"]
                        }
                    },
                    "script": {
                        "source": """
                            0.5 * _score +
                            0.5 * cosineSimilarity(params.query_vector, 'embedding')
                        """,
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            },
            highlight={
                "fields": {
                    "content": {}
                }
            }
        )


  


    hits = res.get("hits", {}).get("hits", [])
    results = []

    for hit in hits:
        src = hit.get("_source", {})

        highlight = hit.get("highlight", {}).get("content", [])
        if highlight:
            snippet = highlight[0]
        else:
            content = src.get("content", "")
            snippet = content[:200].replace("\n", " ") + "..." if content else ""

        results.append({
            "title": src.get("title", ""),
            "url": src.get("url", ""),
            "snippet": snippet,
            "score": hit.get("_score", 0)
        })

    return results
