
import os
import requests

TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("BALE_CHAT_ID")

def send_message(text):
    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    response = requests.post(url, json=data)

    print(response.status_code)
    print(response.text)


send_message("🔔 باید سه‌شنبه نامه ریکال رو بزنی")