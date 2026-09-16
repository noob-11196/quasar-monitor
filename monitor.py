import requests

# 복사해둔 디스코드 웹후크 URL을 아래 큰따옴표 안에 직접 붙여넣으세요!
DISCORD_WEBHOOK = "여기에_디스코드_웹후크_URL을_붙여넣으세요"


def main():
    print("🚀 디스코드 알림 테스트 시작...")
    
    if "여기에" in DISCORD_WEBHOOK or not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK에 디스코드 주소를 직접 넣고 저장해주세요.")
        return

    try:
        data = {"content": "🔔 **[테스트 알림]** 연동 성공! 알림이 정상 작동합니다."}
        resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
        resp.raise_for_status()
        print("✅ 디스코드 알림 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")


if __name__ == "__main__":
    main()
