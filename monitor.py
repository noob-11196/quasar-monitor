import os
import requests

webhook_url = os.environ.get("DISCORD_WEBHOOK")

if not webhook_url:
    print("오류: DISCORD_WEBHOOK 환경변수가 없습니다.")
else:
    data = {
        "content": "🚨 **[테스트 알림]** 퀘이사존 크롤러 및 디스코드 웹후크 연동이 정상 작동합니다!"
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("성공적으로 디스코드 테스트 메시지를 전송했습니다!")
    else:
        print(f"전송 실패. 응답 코드: {response.status_code}, 내용: {response.text}")
