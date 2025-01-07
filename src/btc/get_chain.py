import requests
from datetime import datetime, timedelta
from firebase_admin import firestore, credentials, initialize_app
import os


URL = "https://timechainindex.com/api/entities/entities"
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "../credentials.json"))
initialize_app(cred)
db = firestore.client()
COLLECTION = "whale_activity"

def get_data():
    response = requests.get(URL)
    data = response.json()
    date = data['Date'].split(' ')[0]
    db.collection(COLLECTION).document(date).set(data)

    return data, date

def format_large_number_with_sign(value, add_sign=True):
    sign = "+" if value > 0 and add_sign else ""
    if abs(value) >= 1_000_000_000:
        return f"{sign}{value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{sign}{value / 1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{sign}{value / 1_000:.2f}K"
    else:
        return f"{sign}{value:.2f}"


def generate_message(recent_data, recent_date):
    recent_date = datetime.strptime(recent_date, "%Y-%m-%d")
    dates = []
    docs = db.collection(COLLECTION).stream()
    for doc in docs:
        dates.append(datetime.strptime(doc.id, "%Y-%m-%d"))
    dates.sort()

    files = []    
    offsets = [1, 30]
    actual_offsets = []
    for offset in offsets:
        target_date = recent_date - timedelta(days=offset)
        closest_date = max((date for date in dates if date <= target_date), default = None)
        if closest_date is None:
            closest_date = min(date for date in dates if date > target_date)
        files.append(closest_date)
        actual_offsets.append((recent_date - closest_date).days)

    target_tags = ["CEXs", "ETFs/ETPs"]
    column_data = {tag: {} for tag in target_tags}
    for tag_data in recent_data.get("Tags"):
        if tag_data["Tag"] in target_tags:
            entities = {
                entity.get("Entity"): [entity.get("RemainingBalance")]
                for entity in tag_data.get("Entities")
            }
            top_entities = dict(sorted(
                entities.items(),
                key=lambda item: item[1][0],
                reverse=True
            )[:5])
            column_data[tag_data["Tag"]] = top_entities
    
    for tag in column_data:
        top_entities = column_data[tag]
        for file_date in files:
            file_doc = db.collection(COLLECTION).document(file_date.strftime('%Y-%m-%d')).get()

            file_data = file_doc.to_dict()
            file_entities = {e.get("Entity"): e.get("RemainingBalance") for t in file_data.get("Tags", []) if t["Tag"] == tag for e in t.get("Entities", [])}

            for entity in top_entities:
                top_entities[entity].append(file_entities.get(entity, None))


    msg = f"🐋 *Big Whale Activity (AS OF {recent_date.strftime('%b %d').upper()})*\n\n"

    for tag, data in column_data.items():
        msg += f"🌍 *{tag}*\n"
        msg += "```\n"
        msg += f"{'Exchange':<26}" if "CEXs" == tag else f"{'ETF/ETP':<26}"
        msg += f"{recent_date.strftime('%b %d').upper():<21}"

        msg += f"{(str(actual_offsets[0]) + (' Day Before' if actual_offsets[0] == 1 else ' Days Before')):<21}"
        msg += f"{(str(actual_offsets[1]) + (' Day Before' if actual_offsets[1] == 1 else ' Days Before')):<21}\n"
        msg += "-" * 85 + "\n"

        for entity_name, balances in data.items():
            balance_today = balances[0]
            balance_last_1 = balances[1]
            balance_last_30 = balances[2]

            # Calculate changes
            change_last_1 = balance_today - balance_last_1
            change_last_30 = balance_today - balance_last_30

            # Format the row
            msg += (f"{entity_name:<25} {format_large_number_with_sign(balance_today, False):<20} "
                    f"{format_large_number_with_sign(change_last_1, True):<20} "
                    f"{format_large_number_with_sign(change_last_30, True):<20}\n")
        msg += "```"
    return msg

def get_chain():
    data, date = get_data()
    msg = generate_message(data, date)
    return msg