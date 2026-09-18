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
    
    # 퀘이사존 알뜰구매 게시판 다양한 태그 대응
    items = soup.select("p.tit") or soup.select("a.subject-link") or soup.select("div.market-info-type")
    
    print(f"감지된 게시글 수: {len(items)}")

    if not DISCORD_WEBHOOK_URL:https://discord.com/api/webhooks/1549372299986083910/optPeZzfIdwRajEhfjdBWlK4J1P4bXe5VMUoXgMDbzWapEdKuc8rQP8n_Oi3tTgFR2YL
        print("경고: DISCORD_WEBHOOK 환경변수가 설정되지 않았습니다.")
        return

    sent_count = 0
    # 전체 링크 태그 탐색
    for a_tag in soup.find_all("a", href=True):
        if "/bbs/qb_saleinfo/views/" in a_tag['href']:
            title = a_tag.get_text(strip=True)
            if not title or len(title) < 2:
                continue
                
            link = "https://quasarzone.com" + a_tag['href']
            
            print(f"발견: {title}")
            
            if sent_count < 3:  # 먼저 최신 3개만 테스트 전송
                message = {
                    "content": f"**[핫딜 알림]**\n**제목:** {title}\n**링크:** {link}"
                }
                res = requests.post(DISCORD_WEBHOOK_URL, json=message)
                print(f"디스코드 전송 결과: {res.status_code}")
                sent_count += 1

if __name__ == "__main__":
    fetch_and_notify()

