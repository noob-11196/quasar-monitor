import os
import requests
from bs4 import BeautifulSoup

# =========================
# 설정
# =========================

QUASARZONE_URL = "https://quasarzone.com/bbs/qb_saleinfo"

# 찾고 싶은 단어
KEYWORDS = [
    "RX 9070",
    "9070",
]

# Discord Webhook은 GitHub Secrets에서 가져옵니다.
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        )
    }

    response = requests.get(
        QUASARZONE_URL,
        headers=headers,
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

        if not any(keyword.lower() in title.lower() for keyword in KEYWORDS):
            continue

        if href.startswith("/"):
            href = "https://quasarzone.com" + href

        posts.append({
            "title": title,
            "url": href
        })

    return posts


def send_discord(post):
    if not DISCORD_WEBHOOK:
        print("DISCORD_WEBHOOK이 설정되지 않았습니다.")
        return

    message = (
        "🚨 퀘이사존 새 핫딜 발견!\n\n"
        f"**{post['title']}**\n"
        f"{post['url']}"
    )

    response = requests.post(
        DISCORD_WEBHOOK,
        json={"content": message},
        timeout=15
    )

    response.raise_for_status()


def main():
    posts = get_posts()

    if not posts:
        print("조건에 맞는 글이 없습니다.")
        return

    # GitHub Actions가 이전에 확인한 글을 중복 알림하지 않도록 저장
    old_posts = set()

    if os.path.exists("seen.txt"):
        with open("seen.txt", "r", encoding="utf-8") as f:
            old_posts = set(line.strip() for line in f if line.strip())

    new_posts = []

    for post in posts:
        if post["url"] not in old_posts:
            new_posts.append(post)

    for post in new_posts:
        send_discord(post)
        print("알림:", post["title"])

    # 확인한 글 저장
    with open("seen.txt", "a", encoding="utf-8") as f:
        for post in new_posts:
            f.write(post["url"] + "\n")


if __name__ == "__main__":
    main()
