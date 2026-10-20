import os
import requests
import google.auth
import gspread
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TOKEN = os.environ["BALE_TOKEN"]
CHAT_ID = os.environ["BALE_CHAT_ID"]
SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
TZ = ZoneInfo("Asia/Tehran")

credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(SHEET_ID)

schedule = spreadsheet.worksheet("برنامه شیفت ها").get_all_values()
personnel = spreadsheet.worksheet("پرسنل").get_all_values()

tomorrow = (datetime.now(TZ).date() + timedelta(days=1)).isoformat()

names = {}
for row in personnel[1:]:
    row += [""] * (17 - len(row))
    if row[0] and row[9].strip() == "فعال":
        names[row[0].strip()] = f"{row[1].strip()} {row[2].strip()}".strip()

shifts = []
for row in schedule[1:]:
    row += [""] * (18 - len(row))
    if row[1].strip() != tomorrow:
        continue
    if row[7].strip() == "لغو شده":
        continue

    code = row[2].strip()
    name = names.get(code)
    if not name:
        continue

    start = row[4].strip()
    end = row[5].strip()
    shifts.append((start, name, end))

shifts.sort()

date_text = (datetime.now(TZ).date() + timedelta(days=1)).strftime("%Y-%m-%d")
if shifts:
    lines = [f"📅 برنامه شیفت فردا ({date_text})", ""]
    for start, name, end in shifts:
        lines.append(f"• {start} تا {end} — {name}")
    message = "\n".join(lines)
else:
    message = f"📅 برای فردا ({date_text}) شیفت ثبت‌شده‌ای وجود ندارد."

response = requests.post(
    f"https://tapi.bale.ai/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": message},
    timeout=30,
)
response.raise_for_status()
print(message)
