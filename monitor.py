
import os
import cloudscraper
from bs4 import BeautifulSoup
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

def fetch_and_notify():
    url = "https://quasarzone.com/bbs/qb_saleinfo"
    
    # Cloudflare 우회를 위한 scraper 생성
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # 커스텀 헤더 추가 (GitHub Actions 차단 회피)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    response = scraper.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"페이지를 불러오는데 실패했습니다. 상태 코드: {response.status_code}")
        return

    print("성공적으로 페이지를 불러왔습니다!")
    
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("div.market-type-list tbody tr")
    
    for row in rows:
        title_tag = row.select_one("span.ellipsis-with-reply-count")
        price_tag = row.select_one("span.text-orange")
        link_tag = row.select_one("a.subject-link")
        
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True) if price_tag else "가격 정보 없음"
            link = "https://quasarzone.com" + link_tag['href']
            
            print(f"제목: {title} | 가격: {price}")
            
            if DISCORD_WEBHOOK_URL:
                message = {
                    "content": f"**[핫딜 알림]**\n**제목:** {title}\n**가격:** {price}\n**링크:** {link}"
                }
                requests.post(DISCORD_WEBHOOK_URL, json=message)

if __name__ == "__main__":
    fetch_and_notify()
