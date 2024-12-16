import requests
import telegram
from datetime import datetime
import os
from utils import telegram_utils as telegram


URL = "https://timechainindex.com/api/entities/entities"

def get_data():
    response = requests.get(URL)
    if response.status_code != 200:
        exit()
    data = response.json()

    today = datetime.now().strftime("%Y-%m-%d")
    folder_path = "data/whale_activity"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = os.path.join(folder_path, f"{today}.txt")
    with open(filename, 'w') as file:
        file.write(str(data))

    return data

def format_large_number(value):
    if value >= 1_000_000_000: return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000: return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000: return f"{value / 1_000:.2f}K"
    else: return f"{value:.2f}"

def generate_message(data):
    tags = ["CEXs", "ETFs/ETPs", "Miners"]
    tag_entities = {tag: [] for tag in tags}
    for tag_data in data.get("Tags"):
        if tag_data["Tag"] in tags:
            tag_entities[tag_data["Tag"]].extend(tag_data.get("Entities"))

    # Sort entities within each tag by RemainingBalance and pick the top 5
    for tag in tag_entities:
        tag_entities[tag] = sorted(
            tag_entities[tag],
            key=lambda entity: entity.get("RemainingBalance"),
            reverse=True
        )[:5]

    # Generate the message
    msg = f"📊 *Big Whale Activity ({datetime.now().strftime('%d %b %Y')})*\n"
    msg += "The *TOP 5 entities* with the largest Bitcoin holdings after accounting for all inflows and outflows, showcasing their current influence and capacity in the Bitcoin market.\n\n"
    for tag, entities in tag_entities.items():
        msg += f"🌍 *{tag}*\n"
        for entity in entities:
            entity_name = entity.get("Entity")
            remaining_balance = format_large_number(entity.get("RemainingBalance"))
            msg += f"{entity_name} | {remaining_balance}\n"
        msg += "\n"

    return msg

async def send_chain():
    data = get_data()
    msg = generate_message(data)
    await telegram.send_message(msg)