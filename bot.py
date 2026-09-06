import os
import requests
import time

TOKEN = os.getenv("BALE_TOKEN")

URL = f"https://tapi.bale.ai/bot{TOKEN}/getUpdates"

print("Bot started...")

while True:
    try:
        response = requests.get(URL)

        print("Status:", response.status_code)
        print("Response:", response.text)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)