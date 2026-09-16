import os
from bs4 import BeautifulSoup
import requests

KEYWORDS = ["네이버", "쿠팡", "지마켓", "할인", "특가", "스팀", "무료", "글"]
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_posts():
    if not os.path.exists("html_content.html"):
        print("❌ html_content.html 파일이 존재하지 않습니다.")
        return []

    with open("html_content.html", "r", encoding="utf-8") as f:
        html = f.read()

    print(f"📄 HTML 파일 크기: {len(html)} bytes")
    
    # HTML 시작 부분 300자 출력하여 Cloudflare 차단 페이지인지 확인
    print("--- [다운로드된 HTML 일부 내용] ---")
    print(html[:300].strip())
    print("-----------------------------------")

    soup = BeautifulSoup(html, "html.parser")
    posts = []

    # 전체 링크 태그 탐색
    all_links = soup.find_all("a")
    print(f"🔎 전체 <a> 태그 개수: {len(all_links)}")

    for a in all_links:
        href = a.get("href", "")
        title = a.get_text(" ", strip=True)

        if "/bbs/qb_saleinfo/views/" in href:
            clean_url = href
            if clean_url.startswith("/"):
                clean_url = "https://quasarzone.com" + clean_url

            if not any(p["url"] == clean_url for p in posts):
                posts.append({"title": title, "url": clean_url})

    print(f"🎯 추출된 전체 핫딜 게시글 수: {len(posts)}")
    return posts


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK 비밀값이 설정되지 않았습니다.")
        return

    data = {"content": message}
    resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    resp.raise_for_status()


def main():
    print("🚀 HTML 분석 진행 중...")
    posts = get_posts()

    if not posts:
        print(" 조건에 맞는 게시글이 없습니다.")
        return

    for post in posts[:3]:
        msg = f"🔥 **[핫딜 알림]** {post['title']}\n🔗 {post['url']}"
        send_discord_message(msg)
        print(f"✅ 알림 전송 완료: {post['title']}")


if __name__ == "__main__":
    main()
