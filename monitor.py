import os
import re
import cloudscraper
from bs4 import BeautifulSoup

# 디스코드 웹후크 URL (GitHub Secrets의 DISCORD_WEBHOOK에서 가져옴)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

# URL 설정 (퀘이사존 알뜰구매 게시판)
TARGET_URL = "https://quasarzone.com/bbs/qb_saleinfo"

# ---------------------------------------------------------
# [타겟 품목 및 목표 가격 설정 (원 기준)]
# ---------------------------------------------------------
TARGET_ITEMS = {
    # --- [CPU] 대장급: 41만 원 이하 ---
    "7800X3D": 410000,
    "7600X3D": 410000,
    "7800 X3D": 410000,

    # --- [GPU] RX 9070 계열 목표가: 80만 원 후반 ---
    "9070XT": 890000,
    "9070 XT": 890000,
    "RX9070": 890000,
    "9070": 890000,

    # --- [GPU] RTX 5070 계열 목표가 ---
    "5070Ti": 1150000,
    "5070 Ti": 1150000,
    "RTX5070": 980000,
    "5070": 980000,

    # --- [기타 부품] 특가 조건 설정없이 무조건 알림 ---
    "LIANLI": None,
    "Lianli": None,
    "리안리": None,
    "어엘": None,
    "AORUS ELITE": None,
    "6000 CL30": None,
    "CL30": None,
    "B850M": None,
    "B850": None,
    "850F14GE": None,
    "LEADEX III": None,
    "리덱스": None,
    "슈퍼플라워": None,
    "SuperFlower": None,
    "슈플": None,
    "CH270": None,
    "P12 PWM": None,
    "ARCTIC P12": None,

    # --- 추가 키워드 (그래픽카드 & 램 계열) ---
    "RTX": None,
    "지포스": None,
    "라데온": None,
    "RX": None,
    "그래픽카드": None,
    "RAM": None,
    "DDR4": None,
    "DDR5": None,
    "시금치": None,
    "클레브": None,
    "팀그룹": None,
    "커세어": None,
    "G.SKILL": None,
}

def extract_price(title):
    man_match = re.search(r'(\d+(?:\.\d+)?)\s*만\s*원?', title)
    if man_match:
        return int(float(man_match.group(1)) * 10000)
        
    won_match = re.search(r'([\d,]+)\s*원', title)
    if won_match:
        price_str = won_match.group(1).replace(',', '')
        if price_str.isdigit():
            return int(price_str)
            
    return None

def check_sale_info():
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    response = scraper.get(TARGET_URL)
    if response.status_code != 200:
        print(f"페이지를 불러오는데 실패했습니다. 상태 코드: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    links = soup.find_all("a", href=re.compile(r"/bbs/qb_saleinfo/views/\d+"))
    
    if not links:
        print("게시글을 가져오지 못했습니다.")
        return

    print(f"총 {len(links)}개의 링크 탐색 완료. 키워드 검사 시작...")
    
    found_count = 0
    visited_links = set()

    for link_tag in links:
        title = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        
        if href in visited_links or len(title) < 3:
            continue
        visited_links.add(href)

        full_link = "https://quasarzone.com" + href if href.startswith("/") else href
        title_upper = title.upper()

        for keyword, max_price in TARGET_ITEMS.items():
            if keyword.upper() in title_upper:
                price = extract_price(title)
                
                if max_price is None or price is None or price <= max_price:
                    print(f"[감지 성공] 키워드: {keyword} | 제목: {title}")
                    send_discord_message(scraper, title, full_link, price, max_price)
                    found_count += 1
                    break

    print(f"검사 완료: 총 {found_count}개의 핫딜 알림을 전송했습니다.")

def send_discord_message(scraper, title, link, price, max_price):
    if not DISCORD_WEBHOOK_URL:
        print("디스코드 웹후크 URL이 설정되지 않았습니다.")
        return

    price_info = f"💰 감지 가격: {price:,}원" if price else "💰 가격 정보 미기재 (제목 직접 확인 필요)"
    target_info = f" (목표가: {max_price:,}원 이하)" if max_price else ""

    message = {
        "content": f"🚨 **대박 핫딜 감지!**\n**제목**: {title}\n{price_info}{target_info}\n🔗 [게시글 바로가기]({link})"
    }
    
    try:
        res = scraper.post(DISCORD_WEBHOOK_URL, json=message)
        if res.status_code not in [200, 204]:
            print(f"디스코드 전송 실패. 응답 코드: {res.status_code}")
    except Exception as e:
        print(f"디스코드 전송 중 에러 발생: {e}")

if __name__ == "__main__":
    check_sale_info()
