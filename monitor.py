import os
import re
import requests
from bs4 import BeautifulSoup

# 디스코드 웹후크 URL
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

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

def extract_price(text):
    man_match = re.search(r'(\d+(?:\.\d+)?)\s*만\s*원?', text)
    if man_match:
        return int(float(man_match.group(1)) * 10000)
        
    won_match = re.search(r'([\d,]+)\s*원', text)
    if won_match:
        price_str = won_match.group(1).replace(',', '')
        if price_str.isdigit():
            return int(price_str)
            
    return None

def send_status_message(message):
    if not DISCORD_WEBHOOK_URL:
        print("디스코드 웹후크 URL이 설정되지 않았습니다.")
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"디스코드 전송 실패: {e}")

def check_sale_info():
    try:
        with open("html_content.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("오류: html_content.html 파일을 찾을 수 없습니다.")
        send_status_message("⚠️ **[경고]** HTML 파일을 읽을 수 없어 모니터링이 중단되었습니다.")
        return

    soup = BeautifulSoup(html, "html.parser")
    
    # 퀘이사존 게시글 링크 추출 (경로에 views가 포함된 모든 <a> 태그)
    all_a_tags = soup.find_all("a", href=True)
    links = [a for a in all_a_tags if "/bbs/qb_saleinfo/views/" in a["href"]]
    
    if not links:
        print("게시글을 가져오지 못했습니다.")
        send_status_message("⚠️ **[상태 알림]** 퀘이사존 페이지 파싱 실패 (HTML 태그 확인 필요)")
        return

    print(f"총 {len(links)}개의 게시글 링크 탐색 완료. 키워드 검사 시작...")
    
    found_count = 0
    visited_links = set()

    for link_tag in links:
        href = link_tag.get("href", "")
        if href in visited_links:
            continue
        visited_links.add(href)

        # 게시글 제목 추출
        title = link_tag.get_text(strip=True)
        if len(title) < 3:
            continue

        full_link = "https://quasarzone.com" + href if href.startswith("/") else href
        title_upper = title.upper()

        # 부모 요소를 탐색하여 가격 정보 추출
        parent = link_tag.parent
        price_text = parent.get_text() if parent else title

        for keyword, max_price in TARGET_ITEMS.items():
            if keyword.upper() in title_upper:
                price = extract_price(price_text) or extract_price(title)
                
                if max_price is None or price is None or price <= max_price:
                    print(f"[감지 성공] 키워드: {keyword} | 제목: {title}")
                    
                    price_info = f"💰 감지 가격: {price:,}원" if price else "💰 가격 정보 미기재 (제목 참조)"
                    target_info = f" (목표가: {max_price:,}원 이하)" if max_price else ""
                    
                    msg = f"🚨 **대박 핫딜 감지!**\n**제목**: {title}\n{price_info}{target_info}\n🔗 [게시글 바로가기]({full_link})"
                    send_status_message(msg)
                    found_count += 1
                    break

    print(f"검사 완료: 총 {found_count}개의 핫딜 알림을 전송했습니다.")
    
    # 핫딜이 하나도 안 잡혔을 때 크롤러 생존 확인 알림 전송
    if found_count == 0:
        send_status_message("✅ **[시스템 정기 점검]** 크롤러 정상 작동 중 (현재 조건에 맞는 새로운 핫딜 없음)")

if __name__ == "__main__":
    check_sale_info()
