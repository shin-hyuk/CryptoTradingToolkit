import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests

URL = "https://bitinfocharts.com/bitcoin-distribution-history.html"

RAW_RANGES = [
    "0 - 0.1 BTC",
    "0.1 - 1 BTC",
    "1 - 10 BTC",
    "10 - 100 BTC",
    "100 - 1,000 BTC",
    "1,000 - 10,000 BTC",
    "10,000 - 100,000 BTC",
    "100,000 - 1,000,000 BTC"
]

NEW_RANGES = {
    "0.001 - 1 BTC": ["0 - 0.1 BTC", "0.1 - 1 BTC"],
    "1 - 10 BTC": ["1 - 10 BTC"],
    "10 - 100 BTC": ["10 - 100 BTC"],
    "100+ BTC": ["100 - 1,000 BTC", "1,000 - 10,000 BTC", "10,000 - 100,000 BTC", "100,000 - 1,000,000 BTC"]
}

def merge_data(data):
    merged_data = {}
    for new_range, old_ranges in NEW_RANGES.items():
        merged_data[new_range] = sum(data[old_range] for old_range in old_ranges if old_range in data)
    return merged_data

def get_data_since(start_date):
    data = get_data()

    years_data = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.now()

    while current_date <= end_date:
        date_str = current_date.strftime('%Y/%m/%d')
        if date_str in data:
            row = {"Date": date_str}
            row.update(merge_data({row[0]: row[1] for row in data[date_str]}))
            years_data.append(row)
        current_date += timedelta(days=1)

    df = pd.DataFrame(years_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df


def get_data():
    response = requests.get(URL)
    if response.status_code != 200:
        exit()

    soup = BeautifulSoup(response.content, 'html.parser')
    script = soup.find('script', string=re.compile(r'new Dygraph')).string
    data_string = re.search(r'\[\[new Date\(".*?"\),.*?\]\]', script, re.DOTALL).group(0)
    data = eval(data_string.replace('new Date', '').replace('(', '').replace(')', ''))
    # row ['2024/12/13', 318077, 1073975, 2089601, 4302751, 4353081, 4699187, 2307114, 648734]
    dates = [row[0].replace('"', '') for row in data]
    values = [row[1:] for row in data]

    data = {}
    for date, value_row in zip(dates, values):
        data[date] = [[addr_range, val] for addr_range, val in zip(RAW_RANGES, value_row)]

    data = dict(reversed(data.items()))
    return data

def generate_message(data):
    dates = list(data.keys())

    today_data = merge_data({row[0]: row[1] for row in data[dates[0]]})
    yesterday_data = merge_data({row[0]: row[1] for row in data[dates[1]]})
    day_before_yesterday_data = merge_data({row[0]: row[1] for row in data[dates[2]]})
    last_30_days_data = merge_data({row[0]: row[1] for row in data[dates[30]]})

    addresses = list(NEW_RANGES.keys())
    held_today = [today_data[address] for address in addresses]
    today_changes = [today_data[address] - yesterday_data[address] for address in addresses]
    yesterday_changes = [yesterday_data[address] - day_before_yesterday_data[address] for address in addresses]
    last_30_days_changes = [today_data[address] - last_30_days_data[address] for address in addresses]

    df = pd.DataFrame({
        "BTC Addresses": addresses,
        "# BTC Held Today": held_today,
        f"Today ({dates[0]})": today_changes,
        f"Yesterday ({dates[1]})": yesterday_changes,
        "Last 30 Days": last_30_days_changes,
    })

    msg = f"📊 *Bitcoin Distribution Table*\n\n"
    msg += f"```\n{'BTC Addresses':<20}{'# BTC Held Today':<20}{'Today':<10}{'Yesterday':<15}{'Last 30 Days':<15}\n"
    msg += "-" * 77 + "\n"

    for _, row in df.iterrows():
        addresses = row['BTC Addresses']
        held_today = f"{row['# BTC Held Today']:,}"
        today = f"{int(row[f'Today ({dates[0]})']):+}"
        yesterday = f"{int(row[f'Yesterday ({dates[1]})']):+}"
        last_30_days = f"{int(row['Last 30 Days']):+}"

        msg += f"{addresses:<20}{held_today:<20}{today:<10}{yesterday:<15}{last_30_days:<15}\n"

    msg += "```"

    return msg

def get_distribution():
    data = get_data()
    msg = generate_message(data)
    return msg