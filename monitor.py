import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# 설정
# ==========================================

# 구글 번역 프록시를 이용해 퀘이사존 차단을 완벽히 우회합니다.
TARGET_URL = "https://quasarzone-com.translate.goog/bbs/qb_saleinfo?_x_tr_sl=ko&_x_tr_tl=en&_x_tr_hl=ko"

# 테스트용 키워드 (디스코드 알림 확인 후 원래 찾으시는 키워드로 변경하세요)
KEYWORDS = [
    "네이버",
    "무료",
    "쿠팡",
    "특가"
]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }

    response = requests.get(TARGET_URL, headers=headers, timeout=15)
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

        # 번역 주소 형태를 원래 퀘이사존 주소로 복원
        clean_url = href.split("?")[0].replace("quasarzone-com.translate.goog", "quasarzone.com")
        if clean_url.startswith("/"):
            clean_url = "https://quasarzone.com" + clean_url

        posts.append({
            "title": title,
            "url": clean_url
        })

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
