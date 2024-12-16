import requests
from datetime import datetime, timezone

FNG_ALL_API_URL = "https://api.alternative.me/fng/?limit=0&format=json"
FNG_TODAY_API_URL = "https://api.alternative.me/fng/?limit=1&format=json"


def get_data():
    response = requests.get(FNG_ALL_API_URL)
    data = response.json().get("data")
    for entry in data:
        entry["date"] = datetime.fromtimestamp(int(entry["timestamp"]), tz=timezone.utc).strftime('%Y-%m-%d')
        del entry["timestamp"]
        entry.pop("time_until_update", None)
    return data

def generate_message(data):
    today_data, yesterday_data = data[0], data[1]
    today_index, yesterday_index = int(today_data['value']), int(yesterday_data['value'])
    today_grade = today_data['value_classification'].lower()
    
    if today_index > yesterday_index:
        change = f"Rose to {today_index}"
    elif today_index < yesterday_index:
        change = f"Dropped to {today_index}"
    else:
        change = f"Stayed at {today_index}"

    today_grade = " ".join(word.capitalize() for word in today_grade.split())

    if "fear" in today_grade.lower():
        text = f"**🟩 {today_grade}** - {change}"
    elif "greed" in today_grade.lower():
        text = f"**🟥 {today_grade}** - {change}"
    else:
        text = f"**{today_grade}** - {change}"

    msg = f"⚖️ *Fear and Greed Index*\n"
    msg += f"{text}\n"

    return msg

def get_greed_fear_index():
    data = get_data()
    msg = generate_message(data)
    return msg