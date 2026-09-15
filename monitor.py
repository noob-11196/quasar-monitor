import os
import requests
from bs4 import BeautifulSoup

# 퀘이사존 핫딜 직접 요청
TARGET_URL = "https://quasarzone.com/bbs/qb_saleinfo"

# 테스트용 키워드
KEYWORDS = ["네이버", "무료", "쿠팡", "특가"]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    # 브라우저 직접 접속으로 위장하는 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    response = requests.get(TARGET_URL, headers=headers, timeout=15)
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

        posts.append({"title": title, "url": href})

    return posts


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK 비밀값이 설정되지 않았습니다.")
        return

    data = {"content": message}
    resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    resp.raise_for_status()


def main():
    print("🚀 크롤링 시작...")
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
