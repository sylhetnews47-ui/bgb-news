import feedparser
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

RSS_FEEDS = [
    "https://www.prothomalo.com/feed/",
    "https://www.bd-pratidin.com/rss.xml",
    "https://www.jugantor.com/rss.xml",
    "https://www.kalerkantho.com/rss.xml",
    "https://www.samakal.com/rss.xml",
    "https://www.ittefaq.com.bd/rss.xml",
    "https://www.banglatribune.com/feed",
    "https://www.dhakatribune.com/feed",
    "https://www.thedailystar.net/rss.xml",
]

BGB_KEYWORDS = [
    "বিজিবি", "বি জি বি", "বর্ডার গার্ড", "সীমান্ত রক্ষা বাহিনী",
    "BGB", "Border Guard Bangladesh", "বর্ডারগার্ড", "সীমান্তরক্ষী",
    "বর্ডার গার্ড বাংলাদেশ"
]

DIVISIONS = ["ঢাকা", "চট্টগ্রাম", "রাজশাহী", "খুলনা", "বরিশাল", "সিলেট", "রংপুর", "ময়মনসিংহ"]

def is_bgb(title, summary=""):
    text = (title + " " + summary).lower()
    return any(k.lower() in text for k in BGB_KEYWORDS)

def get_division(text):
    for d in DIVISIONS:
        if d in text:
            return d
    return "অন্যান্য"

def get_battalion(text):
    m = re.search(r'(\d+)\s*(?:বিজিবি|BGB|ব্যাটালিয়ন|সেক্টর)', text, re.I)
    return f"{m.group(1)} বিজিবি" if m else "সাধারণ"

def main():
    news = []
    seen = set()

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries:
                title = e.get("title", "")
                link = e.get("link", "")
                summary = e.get("summary", "") or e.get("description", "")
                if link in seen or not is_bgb(title, summary):
                    continue
                seen.add(link)
                news.append({
                    "id": abs(hash(link)) % 10**10,
                    "title": title.strip(),
                    "link": link,
                    "summary": BeautifulSoup(summary, "html.parser").get_text()[:280],
                    "published": e.get("published", datetime.now().isoformat()),
                    "source": feed.feed.get("title", "Unknown"),
                    "division": get_division(title + " " + summary),
                    "battalion": get_battalion(title + " " + summary),
                    "scraped_at": datetime.now().isoformat()
                })
        except Exception as ex:
            print("Error:", url, ex)

    news.sort(key=lambda x: x["scraped_at"], reverse=True)

    data = {
        "last_updated": datetime.now().isoformat(),
        "total": len(news),
        "news": news
    }

    with open("bgb_news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(news)} news")

if __name__ == "__main__":
    main()
