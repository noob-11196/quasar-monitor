import os
import requests
import xml.etree.ElementTree as ET

# 보안 차단을 뚫는 퀘이사존 RSS 피드 주소
RSS_URL = "https://quasarzone.com/rss/qb_saleinfo"

KEYWORDS = ["네이버", "무료", "쿠팡", "특가"]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }

    response = requests.get(RSS_URL, headers=headers, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    posts = []

    for item in root.findall(".//item"):
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""

        if not title:
            continue

        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue

        posts.append({"title": title, "url": link})

    return posts


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK 비밀값이 설정되지 않았습니다.")
        return

    data = {"content": message}
    resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    resp.raise_for_status()


def main():
    print("🚀 RSS 크롤링 시작...")
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
