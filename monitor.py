import os
import requests
from bs4 import BeautifulSoup

# ⬇️ 아래 큰따옴표("") 안에 복사한 디스코드 웹후크 URL을 붙여넣으세요!
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1549372299986083910/optPeZzfIdwRajEhfjdBWlK4J1P4bXe5VMUoXgMDbzWapEdKuc8rQP8n_Oi3tTgFR2YL"

# 감지할 키워드 목록
KEYWORDS = [
    "9070",
    "9070XT",
    "RX9070",
    "9070 XT",
    "5070",
    "5070Ti",
    "5070 Ti",
    "RTX5070",
]

def send_discord_message(message):
    if "여기에_실제_주소를_붙여넣으세요" in DISCORD_WEBHOOK or not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK 주소를 올바르게 입력해주세요.")
        return False

    data = {"content": message}
    try:
        resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 전송 실패: {e}")
        return False


def get_posts():
    if not os.path.exists("html_content.html"):
        return []

    with open("html_content.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    posts = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/bbs/qb_saleinfo/views/" not in href:
            continue

        title = a.get_text(" ", strip=True)
        if not title or len(title) < 2:
            continue

        # 키워드 검사
        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue

        clean_url = href
        if clean_url.startswith("/"):
            clean_url = "https://quasarzone.com" + clean_url

        if not any(p["url"] == clean_url for p in posts):
            posts.append({"title": title, "url": clean_url})

    return posts


def main():
    print("🚀 디스코드 연동 테스트 진행 중...")

    # 1. 디스코드 연동 테스트 알림 발송
    test_success = send_discord_message(
        "🔔 **[알림 연동 완료]** 퀘이사존 핫딜 크롤러가 정상 작동 중입니다!"
    )
    if test_success:
        print("✅ 디스코드 테스트 알림 전송 성공!")

    # 2. 퀘이사존 키워드 핫딜 수집 및 발송
    posts = get_posts()
    print(f"📌 감지된 키워드 게시글 수: {len(posts)}")

    for post in posts[:3]:
        msg = f"🔥 **[핫딜 감지]** {post['title']}\n🔗 {post['url']}"
        send_discord_message(msg)


if __name__ == "__main__":
    main()
