import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# 설정
# ==========================================

TARGET_URL = "https://api.allorigins.win/raw?url=" + requests.utils.quote("https://quasarzone.com/bbs/qb_saleinfo")

# 테스트용 키워드 (알림 확인 후 원래 키워드로 변경하세요)
KEYWORDS = [
    "네이버",
    "무료",
    "쿠팡"
]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }

    response = requests.get(TARGET_URL, headers=headers, timeout=25)
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
