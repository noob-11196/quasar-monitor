import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# 설정
# ==========================================

# 퀘이사존 핫딜 RSS 피드 주소 (차단 없음)
QUASARZONE_RSS_URL = "https://quasarzone.com/rss/qb_saleinfo"

KEYWORDS = [
    "RX 9070",
    "9070",
    "9070XT",
    "9070 XT"
]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(QUASARZONE_RSS_URL, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")
    items = soup.find_all("item")
    posts = []

    for item in items:
        title = item.find("title").get_text(strip=True) if item.find("title") else ""
        link = item.find("link").get_text(strip=True) if item.find("link") else ""

        if not title or not link:
            continue

        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue

        posts.append({
            "title": title,
            "url": link
        })

    return posts


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("DISCORD_WEBHOOK 환경변수가 설정되지 않았습니다.")
        return

    data = {"content": message}
    resp = requests.post(DISCORD_WEBHOOK, json=data)
    resp.raise_for_status()


def main():
    print("크롤링 시작...")
    posts = get_posts()
    print(f"검색된 게시글 수: {len(posts)}")

    if not posts:
        print("조건에 맞는 게시글이 없습니다.")
        return

    for post in posts:
        msg = f"🔥 **[핫딜 알림]** {post['title']}\n🔗 {post['url']}"
        send_discord_message(msg)
        print(f"알림 전송 완료: {post['title']}")


if __name__ == "__main__":
    main()
