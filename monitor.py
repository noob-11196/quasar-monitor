import os
from bs4 import BeautifulSoup
import requests

# 테스트용 키워드 (알림 도착 확인 후 "RX 9070", "9070XT" 등으로 변경하세요)
KEYWORDS = ["네이버", "쿠팡", "지마켓", "할인", "특가", "스팀"]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    if not os.path.exists("html_content.html"):
        print("❌ HTML 파일을 찾을 수 없습니다.")
        return []

    with open("html_content.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    posts = []

    # 퀘이사존 핫딜 목록의 제목 영역(subject-link)을 직접 조준
    title_elements = soup.select("a.subject-link, a[href*='/bbs/qb_saleinfo/views/']")

    for a in title_elements:
        href = a.get("href", "")
        if "/bbs/qb_saleinfo/views/" not in href:
            continue

        # 제목 텍스트 가져오기 (태그 안의 불필요한 공백 제거)
        title = a.get_text(" ", strip=True)
        if not title or len(title) < 2:
            continue

        # 키워드 포함 여부 검사
        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue

        # URL 풀 주소 생성
        clean_url = href
        if clean_url.startswith("/"):
            clean_url = "https://quasarzone.com" + clean_url

        # 중복 제거
        if not any(p["url"] == clean_url for p in posts):
            posts.append({"title": title, "url": clean_url})

    return posts


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK 비밀값이 설정되지 않았습니다.")
        return

    data = {"content": message}
    resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    resp.raise_for_status()


def main():
    print("🚀 HTML 파싱 시작...")
    posts = get_posts()
    print(f"📌 검색된 게시글 수: {len(posts)}")

    if not posts:
        print("조건에 맞는 게시글이 없습니다.")
        return

    # 테스트를 위해 검색된 게시글 중 최대 3개 전송
    for post in posts[:3]:
        msg = f"🔥 **[핫딜 알림]** {post['title']}\n🔗 {post['url']}"
        send_discord_message(msg)
        print(f"✅ 알림 전송 완료: {post['title']}")


if __name__ == "__main__":
    main()
