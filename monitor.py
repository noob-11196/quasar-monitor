import os
import cloudscraper
from bs4 import BeautifulSoup

TARGET_URL = "https://quasarzone.com/bbs/qb_saleinfo"

# 테스트용 키워드
KEYWORDS = [
    "네이버",
    "무료",
    "쿠팡",
    "특가"
]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    # Cloudflare 차단을 우회하는 scraper 생성
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    response = scraper.get(TARGET_URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    for a in soup.find_all("a", href=True):
        title = a.get_text(" ", strip=True)
        href = a["href"]

        if not title or "/bbs/qb_saleinfo/views/" not in href:
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
        print("❌ ERROR: DISCORD_WEBHOOK 비밀값이 설정되지 않았습니다.")
        return

    scraper = cloudscraper.create_scraper()
    data = {"content": message}
    resp = scraper.post(DISCORD_WEBHOOK, json=data, timeout=5)
    resp.raise_for_status()


def main():
    print("🚀 Cloudscraper 크롤링 시작...")
    try:
        posts = get_posts()
        print(f"📌 검색된 게시글 수: {len(posts)}")

        if not posts:
            print("조건에 맞는 게시글이 없습니다.")
            return

        for post in posts[:3]:
            msg = f"🔥 **[핫딜 알림]** {post['title']}\n🔗 {post['url']}"
            send_discord_message(msg)
            print(f"✅ 알림 전송 완료: {post['title']}")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")


if __name__ == "__main__":
    main()
