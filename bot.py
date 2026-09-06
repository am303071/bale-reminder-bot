import os
import requests

TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("BALE_CHAT_ID")

MESSAGE = "🧪 تست ربات: ارسال پیام با موفقیت انجام شد."


def send_message():
    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": MESSAGE
    }

    response = requests.post(url, json=data)

    print("Status:", response.status_code)
    print("Response:", response.text)


send_message()