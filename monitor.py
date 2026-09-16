import os
import re
from bs4 import BeautifulSoup
import requests

# 테스트용 키워드 (알림 수신 확인 후 "RX 9070", "9070XT"로 변경하세요)
KEYWORDS = ["네이버", "무료", "쿠팡", "특가", "할인", "배송"]

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    if not os.path.exists("html_content.html"):
        print("❌ HTML 파일을 찾을 수 없습니다.")
        return []

    with open("html_content.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    posts = []

    # 퀘이사존 핫딜 게시물 제목 클래스 및 a 태그 유연하게 탐색
    for a in soup.find_all("a", href=True):
        href = a["href"]

        # 핫딜 게시물 상세 링크 조건 (views)
        if "qb_saleinfo/views" not in href:
            continue

        # 텍스트 정제
        title = a.get_text(" ", strip=True)
        
        # 품절 표시나 불필요한 태그 정리
        if not title or len(title) < 2:
            continue

        # 키워드 매칭 검사
        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue

        # URL 정상화
        clean_url = href
        if clean_url.startswith("/"):
            clean_url = "https://quasarzone.com" + clean_url

        # 중복 등록 방지
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

    # 테스트용으로 최대 3개 전송
    for post in posts[:3]:
        msg = f"🔥 **[핫딜 알림]** {post['title']}\n🔗 {post['url']}"
        send_discord_message(msg)
        print(f"✅ 알림 전송 완료: {post['title']}")


if __name__ == "__main__":
    main()
