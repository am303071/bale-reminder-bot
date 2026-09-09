import os
import requests
import datetime
import gspread
import google.auth
from zoneinfo import ZoneInfo


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

iran_time = datetime.datetime.now(ZoneInfo("Asia/Tehran"))

today = iran_time.date()
tomorrow = today + datetime.timedelta(days=1)

today_str = today.strftime("%Y-%m-%d")
tomorrow_str = tomorrow.strftime("%Y-%m-%d")


# =========================
# خواندن اطلاعات Sheet
# =========================

rows = sheet.get_all_values()

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
# اطلاعات امروز
# =========================

if today_data:
    jalali_today = str(
        today_data.get("تاریخ شمسی", "")
    ).strip()

    day_today = str(
        today_data.get("روز", "")
    ).strip()

else:
    jalali_today = ""
    day_today = ""


# =========================
# ساخت پیام
# =========================

message = "📋 ━━━ برنامه روزانه ━━━\n\n"

message += f"📅 {day_today}  |  {jalali_today or today_str}\n\n"


# =========================
# کارهای امروز
# =========================

message += "📝 کارهای امروز\n"

if today_data:

    tasks = str(
        today_data.get("کارهای امروز", "")
    ).strip()

    if tasks:
        message += f"└ {tasks}\n\n"
    else:
        message += "└ موردی ثبت نشده\n\n"

else:

    message += "└ اطلاعاتی ثبت نشده\n\n"


# =========================
# اطلاعات فردا
# =========================

if tomorrow_data:

    jalali_tomorrow = str(
        tomorrow_data.get("تاریخ شمسی", "")
    ).strip()

    day_tomorrow = str(
        tomorrow_data.get("روز", "")
    ).strip()

else:

    jalali_tomorrow = ""
    day_tomorrow = ""


# =========================
# شیفت فردا
# =========================

message += "👥 ━━━ شیفت فردا ━━━\n"

message += (
    f"📅 {day_tomorrow}  |  "
    f"{jalali_tomorrow or tomorrow_str}\n\n"
)


if tomorrow_data:

    morning = str(
        tomorrow_data.get("شیفت صبح", "")
    ).strip()

    evening = str(
        tomorrow_data.get("شیفت عصر", "")
    ).strip()

    off = str(
        tomorrow_data.get("آف", "")
    ).strip()

    leave = str(
        tomorrow_data.get("مرخصی", "")
    ).strip()


    # شیفت صبح
    message += "🌅 صبح\n"
    message += f"└ {morning or 'ثبت نشده'}\n\n"


    # شیفت عصر
    message += "🌇 عصر\n"
    message += f"└ {evening or 'ثبت نشده'}\n\n"


    # آف
    message += "🛌 آف\n"
    message += f"└ {off or 'ندارد'}\n\n"


    # مرخصی
    message += "🏖 مرخصی\n"

    if leave and leave != "—":
        message += f"└ {leave}\n\n"
    else:
        message += "└ ندارد\n\n"

else:

    message += "└ اطلاعات شیفت فردا ثبت نشده\n\n"


# =========================
# یادآوری مخصوص سه‌شنبه
# =========================

if today.weekday() == 1:

    message += "🔔 ━━━ یادآوری ━━━\n"
    message += "└ امروز نامه ریکال هفته زده شود"


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
