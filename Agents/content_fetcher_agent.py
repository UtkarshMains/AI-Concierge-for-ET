from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import feedparser
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

app = FastAPI()

# -------- Load Model --------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------- RSS Sources --------
RSS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    "https://economictimes.indiatimes.com/news/rssfeeds/1715249553.cms",
    "https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/5575607.cms",
    "https://economictimes.indiatimes.com/wealth/rssfeeds/837555174.cms"
]

# -------- Storage --------
article_store = []
index = None


# -------- Request Model --------
class CategoryRequest(BaseModel):
    categories: List[str]


# -------- Fetch Articles --------
def fetch_all_articles(limit_per_feed=20):
    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:limit_per_feed]:
            articles.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link
            })

    return articles


# -------- Build FAISS Index --------
def build_index():
    global index, article_store

    article_store = fetch_all_articles()

    # combine title + summary
    texts = [
        a["title"] + " " + a["summary"]
        for a in article_store
    ]

    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True
    )

    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(f"✅ Indexed {len(article_store)} articles")


# -------- Search Articles --------
def search_articles(query_text, top_k=6):

    global index, article_store

    if index is None:
        raise RuntimeError("FAISS index not initialized")

    query_embedding = model.encode(
        [query_text],
        normalize_embeddings=True
    )

    query_embedding = np.array(query_embedding).astype("float32")

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for idx in indices[0]:
        if idx != -1 and idx < len(article_store):
            results.append(article_store[idx])

    return results


# -------- API: Fetch Content --------
@app.post("/fetch-content")
def fetch_content(data: CategoryRequest):

    categories = data.categories

    # Convert categories to search query
    query = " ".join(categories) 

    articles = search_articles(query, top_k=6)

    return {
        "recommended_categories": categories,
        "articles": articles
    }


# -------- INIT --------
@app.on_event("startup")
def startup_event():
    build_index()