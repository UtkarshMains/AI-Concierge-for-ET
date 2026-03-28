import requests
from bs4 import BeautifulSoup

def scrape_et_articles_simple(url="https://economictimes.indiatimes.com/"):
    articles = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.select("a[href*='articleshow']")

    seen = set()

    for link in links:
        href = link.get("href")

        if not href:
            continue

        if not href.startswith("http"):
            href = "https://economictimes.indiatimes.com" + href

        if href in seen:
            continue
        seen.add(href)

        try:
            article_res = requests.get(href, headers=headers)
            article_soup = BeautifulSoup(article_res.text, "html.parser")

            # Title
            title_tag = article_soup.find("h1")
            title = title_tag.text.strip() if title_tag else ""

            # ✅ FIXED CONTENT EXTRACTION
            content = ""
            selectors = [
                "div.artText p",
                "div.Normal p",
                "div.articleBlock p",
                "section p"
            ]

            for sel in selectors:
                paragraphs = article_soup.select(sel)
                if paragraphs:
                    content = " ".join([p.get_text(strip=True) for p in paragraphs])
                    if len(content) > 100:
                        break

            articles.append({
                "Title": title,
                "content": content,
                "link": href
            })

            if len(articles) >= 5:
                break

        except Exception as e:
            continue

    return articles
print(scrape_et_articles_simple())