import requests
from typing import List
from src.models import NewsItem
from datetime import datetime




def parse_newsapi_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None

#Function which parser json
def load_json_url(url: str, timeout: int = 30) -> List[NewsItem]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/133.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    raw_data = response.json()

    news_items = []

    for item in raw_data.get("articles", []):  # ✅ ключ articles, не items
        try:
            title = item.get("title", "Without title")
            summary = item.get("description") or item.get("content") or ""
            link = item.get("url")
            published = parse_newsapi_date(item.get("publishedAt"))

            news = NewsItem(
                title=title,
                summary=summary,
                link=link,
                published=published
            )
            news_items.append(news)
        except Exception as e:
            print(f"Error during processing: {e} | raw item: {item}")

    return news_items



#Function for processing dates
def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        return None
