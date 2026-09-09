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

today = datetime.date.today()
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

        date_value = str(row.get("تاریخ", "")).strip()

        # تبدیل فرمت‌های رایج تاریخ
        date_value = date_value.replace("/", "-")

        if date_value.startswith(today_str):
            today_data = row

        if date_value.startswith(tomorrow_str):
            tomorrow_data = row


# =========================
# ساخت پیام
# =========================

message = f"📅 برنامه امروز — {today_str}\n\n"


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

message += f"👥 شیفت فردا — {tomorrow_str}\n\n"

if tomorrow_data:

    morning = str(tomorrow_data.get("شیفت صبح", "")).strip()
    evening = str(tomorrow_data.get("شیفت عصر", "")).strip()
    leave = str(tomorrow_data.get("مرخصی", "")).strip()

    message += f"🌅 صبح: {morning or 'ثبت نشده'}\n"
    message += f"🌇 عصر: {evening or 'ثبت نشده'}\n"

    if leave and leave != "—":
        message += f"🏖 مرخصی: {leave}\n"

else:

    message += "اطلاعات شیفت فردا ثبت نشده.\n"


# =========================
# Reminder مخصوص دوشنبه
# =========================

if today.weekday() == 0:

    message += "\n🔔 باید سه‌شنبه نامه ریکال رو بزنی"


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
