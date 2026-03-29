from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Define Categories --------
CATEGORIES = {
    "Stock Market": "stock trading equities shares nifty sensex technical analysis",
    "Mutual Funds": "sip mutual funds long term investment portfolio wealth",
    "Startups": "startup funding founders entrepreneurship venture capital",
    "Business News": "corporate news companies industry updates business headlines",
    "Personal Finance": "saving money budgeting tax planning personal finance basics",
    "Economy": "inflation gdp economic policy interest rates macro economy",
    "Explainers": "simple explanation beginner guides easy finance concepts",
    "Trending": "breaking news quick updates latest headlines trending topics"
}
# Extract category names (used for mapping embeddings → names)
category_names = list(CATEGORIES.keys())

# -------- Precompute Category Embeddings --------
# Load once at startup
@app.on_event("startup")
def load_model():
    global model, category_embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    category_names = list(CATEGORIES.keys())
    category_embeddings = model.encode(list(CATEGORIES.values()))


# -------- Request Model --------
class UserInput(BaseModel):
    user_type: str
    user_type_other: str | None = None
    interests: List[str]
    investments: List[str]
    news_type: str
    frequency: str
    goal: str


# -------- Build User Profile --------
def build_user_profile(data: UserInput):

    user_type = data.user_type
    if user_type.lower() == "other" and data.user_type_other:
        user_type = data.user_type_other  # 🔥 dynamic handling

    text = f"""
    {user_type}
    interested in {' '.join(data.interests)}
    invests in {' '.join(data.investments)}
    prefers {data.news_type}
    reads {data.frequency}
    goal {data.goal}
    """

    return text.lower()


# -------- Cosine Similarity --------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# -------- API --------
@app.post("/recommend")
def recommend(data: UserInput):

    profile_text = build_user_profile(data)

    user_embedding = model.encode([profile_text])[0]

    # Compute similarity with each category
    scores = []
    for idx, cat_emb in enumerate(category_embeddings):
        sim = cosine_similarity(user_embedding, cat_emb)
        scores.append((category_names[idx], sim))

    # Sort & get top 3
    scores.sort(key=lambda x: x[1], reverse=True)
    top_3 = [cat for cat, _ in scores[:3]]

    # Call content fetcher API
    articles_response = requests.post(
        "http://localhost:8001/fetch-content",
        json={"categories": top_3}
    )

    articles = articles_response.json()

    return {
        "recommended_categories": top_3,
        "articles": articles["articles"]
    }