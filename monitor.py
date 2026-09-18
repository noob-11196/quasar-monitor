import os
from bs4 import BeautifulSoup
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

def fetch_and_notify():
    file_path = "html_content.html"
    
    if not os.path.exists(file_path):
        print("HTML 파일을 찾을 수 없습니다.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        html_data = f.read()

    print("성공적으로 HTML 파일 읽기 완료!")
    soup = BeautifulSoup(html_data, "html.parser")
    
    # 퀘이사존 게시글 목록 선택
    rows = soup.select("table tbody tr")
    if not rows:
        rows = soup.select("div.market-type-list div.market-info-type")

    print(f"감지된 게시글 수: {len(rows)}")

    if not DISCORD_WEBHOOK_URL:
        print("경고: DISCORD_WEBHOOK 환경변수가 설정되지 않았습니다.")

    sent_count = 0
    for row in rows:
        title_tag = row.select_one("span.ellipsis-with-reply-count") or row.select_one("a.subject-link")
        price_tag = row.select_one("span.text-orange") or row.select_one("span.market-price")
        link_tag = row.select_one("a.subject-link") or row.select_one("a[href*='/bbs/qb_saleinfo/views/']")
        
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True) if price_tag else "가격 정보 없음"
            
            href = link_tag['href']
            link = href if href.startswith("http") else "https://quasarzone.com" + href
            
            print(f"발견: {title} | 가격: {price}")
            
            if DISCORD_WEBHOOK_URL and sent_count < 3:  # 테스트를 위해 상위 3개만 먼저 전송
                message = {
                    "content": f"**[핫딜 알림]**\n**제목:** {title}\n**가격:** {price}\n**링크:** {link}"
                }
                res = requests.post(DISCORD_WEBHOOK_URL, json=message)
                print(f"디스코드 전송 결과: {res.status_code}")
                sent_count += 1

if __name__ == "__main__":
    fetch_and_notify()
