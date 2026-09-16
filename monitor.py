import os
from bs4 import BeautifulSoup
import requests

KEYWORDS = ["네이버", "무료", "쿠팡", "특가"]
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    if not os.path.exists("html_content.html"):
        print("❌ HTML 파일을 찾을 수 없습니다.")
        return []

    with open("html_content.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
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
    print("🚀 HTML 파일 분석 시작...")
    posts = get_posts()
    print(f"📌 검색된 게시글 수: {len(posts)}")

    if not posts:
        print("조건에 맞는 게시글이 없습니다.")
        return

    for post in posts[:3]:
        msg = f"🔥 **[핫딜 알림]** {post['title']}\n🔗 {post['url']}"
        send_discord_message(msg)
        print(f"✅ 알림 전송 완료: {post['title']}")


if __name__ == "__main__":
    main()
