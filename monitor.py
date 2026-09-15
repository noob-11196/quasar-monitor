import os
import cloudscraper
from bs4 import BeautifulSoup

# ==========================================
# 설정
# ==========================================

QUASARZONE_URL = "https://quasarzone.com/bbs/qb_saleinfo"

KEYWORDS = [
    "RX 9070",
    "9070",
    "9070XT",
    "9070 XT"
]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    # Cloudflare 차단을 우회하는 우회용 스크래퍼 생성
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    response = scraper.get(QUASARZONE_URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    for a in soup.find_all("a", href=True):
        title = a.get_text(" ", strip=True)
        href = a["href"]

        if not title:
            continue

        if "/bbs/qb_saleinfo/views/" not in href:
            continue

        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue

        if href.startswith("/"):
            href = "https://quasarzone.com" + href

        posts.append({
            "title": title,
            "url": href
        })

    return posts


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("DISCORD_WEBHOOK 환경변수가 설정되지 않았습니다.")
        return

    import requests
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
