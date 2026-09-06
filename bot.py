import os
import time
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("BALE_CHAT_ID")

TIMEZONE = ZoneInfo("Asia/Tehran")

MESSAGE = "🔔 باید سه‌شنبه نامه ریکال رو بزنی"


def send_message():
    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": MESSAGE
    }

    response = requests.post(url, json=data)

    print("Status:", response.status_code)
    print("Response:", response.text)


def get_next_monday():
    now = datetime.now(TIMEZONE)

    days_until_monday = (7 - now.weekday()) % 7

    next_monday = now.replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0
    ) + timedelta(days=days_until_monday)

    if next_monday <= now:
        next_monday += timedelta(days=7)

    return next_monday


print("🤖 Bale Reminder Bot Started")

while True:
    try:
        next_run = get_next_monday()
        now = datetime.now(TIMEZONE)

        wait_seconds = (next_run - now).total_seconds()

        print("Next reminder:", next_run.strftime("%Y-%m-%d %H:%M"))

        time.sleep(wait_seconds)

        send_message()

        # جلوگیری از ارسال دوباره در همان اجرا
        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)