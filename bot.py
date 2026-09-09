import os
import requests
import datetime
import gspread
import google.auth


# =========================
# تنظیمات
# =========================

TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("BALE_CHAT_ID")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


# =========================
# اتصال به Google Sheets
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

credentials, project = google.auth.default(scopes=SCOPES)

gc = gspread.authorize(credentials)

spreadsheet = gc.open_by_key(SHEET_ID)
sheet = spreadsheet.sheet1


# =========================
# تاریخ امروز و فردا
# =========================

from zoneinfo import ZoneInfo

iran_time = datetime.datetime.now(ZoneInfo("Asia/Tehran"))

today = iran_time.date()
tomorrow = today + datetime.timedelta(days=1)

today_str = today.strftime("%Y-%m-%d")
tomorrow_str = tomorrow.strftime("%Y-%m-%d")

# =========================
# خواندن اطلاعات Sheet
# =========================

rows = sheet.get_all_values()

print("ROWS FROM SHEET:")
print(rows)

today_data = None
tomorrow_data = None

if rows:
    headers = rows[0]

    for values in rows[1:]:
        row = dict(zip(headers, values))

        date_value = str(row.get("تاریخ میلادی", "")).strip()
        date_value = date_value.replace("/", "-")

        if date_value == today_str:
            today_data = row

        if date_value == tomorrow_str:
            tomorrow_data = row

# =========================
# ساخت پیام
# =========================

jalali_today = today_data.get("تاریخ شمسی", "").strip() if today_data else ""
day_today = today_data.get("روز", "").strip() if today_data else ""

message = f"📅 برنامه امروز\n{day_today} {jalali_today or today_str}\n\n"

# کارهای امروز
if today_data:

    tasks = str(today_data.get("کارهای امروز", "")).strip()

    if tasks:
        message += "📝 کارهای امروز:\n"
        message += tasks + "\n\n"
    else:
        message += "📝 کارهای امروز:\nموردی ثبت نشده.\n\n"

else:

    message += "📝 کارهای امروز:\nاطلاعاتی برای امروز ثبت نشده.\n\n"


# =========================
# شیفت فردا
# =========================

jalali_today = today_data.get("تاریخ شمسی", "").strip() if today_data else ""
day_today = today_data.get("روز", "").strip() if today_data else ""

message = f"📅 برنامه امروز\n{day_today} {jalali_today or today_str}\n\n"

if tomorrow_data:

    morning = str(tomorrow_data.get("شیفت صبح", "")).strip()
    evening = str(tomorrow_data.get("شیفت عصر", "")).strip()
    off = str(tomorrow_data.get("آف", "")).strip()
    leave = str(tomorrow_data.get("مرخصی", "")).strip()

    message += f"🌅 صبح: {morning or 'ثبت نشده'}\n"
    message += f"🌇 عصر: {evening or 'ثبت نشده'}\n"
    message += f"🛌 آف: {off or 'ندارد'}\n"

    if leave and leave != "—":
        message += f"🏖 مرخصی: {leave}\n"

else:

    message += "اطلاعات شیفت فردا ثبت نشده.\n"


# =========================
# Reminder مخصوص سه شنبه
# =========================

if today.weekday() == 1:

    message += "\n🔔 امروز نامه ریکال هفته زده شود"


# =========================
# ارسال پیام به بله
# =========================

url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:", response.text)
