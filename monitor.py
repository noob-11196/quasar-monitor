import os
import re
import requests
from bs4 import BeautifulSoup

# 디스코드 웹후크 URL (GitHub Secrets에서 가져옴)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# URL 설정 (퀘이사존 알뜰구매 게시판)
TARGET_URL = "https://quasarzone.com/bbs/qb_saleinfo"

# ---------------------------------------------------------
# [타겟 품목 및 목표 가격 설정 (원 기준)]
# ---------------------------------------------------------
TARGET_ITEMS = {
    # --- [CPU] 목표가: 41만 원 이하 ---
    "7800X3D": 410000,
    "78003D": 410000,
    "7800 X3D": 410000,

    # --- [GPU] 9070 XT 계열 목표가: 89만 원 이하 (80만원대 감지) ---
    "9070XT": 890000,
    "9070 XT": 890000,
    "RX9070": 800000,
    "9070": 800000,

    # --- [GPU] RTX 5070 계열 목표가 ---
    "5070Ti": 1150000,
    "5070 Ti": 1150000,
    "RTX5070": 900000,
    "5070": 900000,

    # --- [기타 부품] 특가 뜨면 금액 상관없이 무조건 알림 ---
    "LQ360": None,
    "B850M": None,
    "B850": None,
    "어엘": None,
    "AORUS ELITE": None,
    "6000 CL30": None,
    "CL30": None,
    "850F14GE": None,
    "LEADEX III": None,
    "리덱스": None,
    "슈퍼플라워": None,
    "SuperFlower": None,
    "CH270": None,
    "P12 PWM": None,
    "ARCTIC P12": None
}

def extract_price(title):
    """제목에서 가격(숫자)을 추출하는 함수"""
    # 1) '숫자 + 만원' 형태 (예: 40만원 -> 400000)
    man_match = re.search(r'(\d+(?:\.\d+)?)\s*만\s*원?', title)
    if man_match:
        return int(float(man_match.group(1)) * 10000)
        
    # 2) '숫자 + 원' 또는 '쉼표 포함 숫자' 형태 (예: 400,000원 -> 400000)
    won_match = re.search(r'([\d,]+)\s*원', title)
    if won_match:
        price_str = won_match.group(1).replace(',', '')
        if price_str.isdigit():
            return int(price_str)
            
    return None

def check_sale_info():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(TARGET_URL, headers=headers)
    if response.status_code != 200:
        print(f"페이지를 불러오는데 실패했습니다. 상태 코드: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    posts = soup.select("div.market-type-list tbody tr")

    for post in posts:
        title_tag = post.select_one("span.ellipsis-with-type-line")
        link_tag = post.select_one("a.subject-link")

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        title_upper = title.upper()
        link = "https://quasarzone.com" + link_tag["href"]

        # 키워드 및 가격 검사
        for keyword, max_price in TARGET_ITEMS.items():
            if keyword.upper() in title_upper:
                price = extract_price(title)
                
                # 조건 판별:
                # 1. 가격 제한이 없는 품목(None)인 경우 -> 알림 전송
                # 2. 제목에 가격이 안 적혀있는 경우(None) -> 놓치지 않게 알림 전송
                # 3. 추출된 가격이 목표가 이하인 경우 -> 알림 전송
                if max_price is None or price is None or price <= max_price:
                    send_discord_message(title, link, price, max_price)
                    break

def send_discord_message(title, link, price, max_price):
    if not DISCORD_WEBHOOK_URL:
        print("디스코드 웹후크 URL이 설정되지 않았습니다.")
        return

    price_info = f"💰 감지 가격: {price:,}원" if price else "💰 가격 정보 미기재 (제목 직접 확인 필요)"
    target_info = f" (목표가: {max_price:,}원 이하)" if max_price else ""

    message = {
        "content": f"🚨 **대박 핫딜 감지!**\n**제목**: {title}\n{price_info}{target_info}\n🔗 [게시글 바로가기]({link})"
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=message)

if __name__ == "__main__":
    check_sale_info()
