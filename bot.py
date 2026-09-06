import os
import requests

TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("BALE_CHAT_ID")

MESSAGE = "🔔 باید سه‌شنبه نامه ریکال رو بزنی"

url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:", response.text)
