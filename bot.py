import os
import requests
import google.auth
import gspread
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

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

today = datetime.now(TZ).date()

names = {}
for row in personnel[1:]:
    row += [""] * (17 - len(row))
    if row[0].strip() and row[9].strip() == "فعال":
        names[row[0].strip()] = (
            f"{row[1].strip()} {row[2].strip()}".strip()
        )

all_shifts = defaultdict(list)

for row in schedule[1:]:
    row += [""] * (18 - len(row))

    if not row[1].strip() or row[7].strip() == "لغو شده":
        continue

    try:
        shift_date = datetime.strptime(
            row[1].strip(), "%Y-%m-%d"
        ).date()
    except ValueError:
        continue

    code = row[2].strip()
    name = names.get(code)
    if not name:
        continue

    all_shifts[code].append({
        "date": shift_date,
        "name": name,
        "start": row[4].strip(),
        "end": row[5].strip(),
    })


def send_message(message):
    response = requests.post(
        f"https://tapi.bale.ai/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=30,
    )
    response.raise_for_status()


def send_daily():
    target = today + timedelta(days=1)
    shifts = []

    for items in all_shifts.values():
        for shift in items:
            if shift["date"] == target:
                shifts.append(shift)

    shifts.sort(key=lambda x: x["start"])
    lines = [f"📅 برنامه شیفت فردا ({target.isoformat()})", ""]

    for shift in shifts:
        lines.append(
            f"• {shift['start']} تا {shift['end']} — {shift['name']}"
        )

    if not shifts:
        lines.append("شیفت ثبت‌شده‌ای وجود ندارد.")

    send_message("\n".join(lines))


def send_period(start_date, end_date, title):
    for code, items in all_shifts.items():
        person_shifts = [
            s for s in items
            if start_date <= s["date"] <= end_date
        ]
        person_shifts.sort(key=lambda x: (x["date"], x["start"]))

        if not person_shifts:
            continue

        name = names[code]
        lines = [
            f"📅 {title}",
            f"👤 {name}",
            ""
        ]

        for shift in person_shifts:
            date_text = shift["date"].strftime("%Y-%m-%d")
            lines.append(
                f"• {date_text}: {shift['start']} تا {shift['end']}"
            )

        send_message("\n".join(lines))


# اجرای دستی با متغیر REPORT_MODE؛ در حالت عادی فقط برنامه فردا
mode = os.getenv("REPORT_MODE", "daily")

if mode == "daily":
    send_daily()

elif mode == "weekly":
    start = today + timedelta(days=1)
    end = start + timedelta(days=6)
    send_period(start, end, f"برنامه هفتگی ({start} تا {end})")

elif mode == "monthly":
    first_next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_next_month = (
        (first_next_month.replace(day=28) + timedelta(days=4))
        .replace(day=1) - timedelta(days=1)
    )
    send_period(
        first_next_month,
        last_next_month,
        f"برنامه ماهانه {first_next_month.strftime('%Y-%m')}"
    )

print(f"گزارش {mode} ارسال شد.")
