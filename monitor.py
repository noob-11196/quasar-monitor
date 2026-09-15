import os
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

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
    # 보안 차단을 우회하기 위한 실제 Chrome 브라우저 상세 헤더
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'referer': 'https://quasarzone.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    response = curl_requests.get(
        QUASARZONE_URL,
        headers=headers,
        impersonate="chrome120",
        timeout=15
    )
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
