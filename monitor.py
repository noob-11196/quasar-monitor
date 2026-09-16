import os
import requests

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK Secrets가 설정되지 않았습니다.")

    data = {"content": message}
    resp = requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    resp.raise_for_status()


def main():
    print("🚀 디스코드 알림 테스트 시작...")
    try:
        msg = "🔔 **[테스트 알림]** 깃허브 액션과 디스코드 연동이 정상적으로 완료되었습니다!"
        send_discord_message(msg)
        print("✅ 디스코드 알림 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")


if __name__ == "__main__":
    main()
