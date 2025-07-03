import feedparser
import requests
from datetime import datetime, timedelta

# === Teams Webhook URL (von dir aus Teams kopieren) ===
TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/..."  # <== Hier deine URL einfügen

# === RSS-Feeds ===
feeds = {
    "Smashing Magazine": "https://www.smashingmagazine.com/feed/",
    "t3n": "https://t3n.de/rss.xml",
    "Golem": "https://www.golem.de/rss.php?feed=RSS2.0",
}

# === Beiträge aus den letzten 24 Stunden sammeln ===
def fetch_recent_entries():
    recent = []
    cutoff = datetime.utcnow() - timedelta(days=1)

    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if not published:
                continue
            pub_date = datetime(*published[:6])
            if pub_date > cutoff:
                recent.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "date": pub_date.strftime("%Y-%m-%d %H:%M"),
                })
    return sorted(recent, key=lambda x: x["date"], reverse=True)

# === Nachricht an Teams senden ===
def post_to_teams(entries):
    if not entries:
        return

    message = "**📰 Tägliche Tech-News**\n\n"
    for entry in entries:
        message += f"• **[{entry['title']}]({entry['link']})** – *{entry['source']}*\n"

    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "Tägliche Tech-News",
        "themeColor": "0078D7",
        "title": "Tägliche Tech-News",
        "text": message
    }

    response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
    print("Posted to Teams:", response.status_code)

# === Hauptprogramm ===
if __name__ == "__main__":
    entries = fetch_recent_entries()
    post_to_teams(entries)
