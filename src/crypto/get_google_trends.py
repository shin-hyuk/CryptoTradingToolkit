from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
from datetime import datetime, timedelta
import random
import time

LIST = ['Bitcoin', 'Ethereum', 'Solana']

def get_data():
    pytrends = TrendReq()
    timeframe = 'today 1-m'
    pytrends.build_payload(LIST, timeframe=timeframe)

    while True:
        try:
            data = pytrends.interest_over_time()
            break
        except TooManyRequestsError:
            sleep_time = random.uniform(5, 10)
            print(f"Too many requests. Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
    
    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    data = data[(data.index >= start_date) & (data.index <= end_date)]

    return data

def generate_message(data):
    normalized_trends = data[LIST].apply(lambda x: (x / x.max()) * 100, axis=0)
    normalized_trends['date'] = normalized_trends.index
    today_values, yesterday_values = normalized_trends.iloc[-1], normalized_trends.iloc[-2]

    msg = f"📊 *Daily Crypto Trend ({datetime.now().strftime('%d %b %Y')})*\nIndex Scale: 0-100\n\n🔍 *Trending Crypto Searches*\n"

    for crypto in LIST:
        today = today_values[crypto]
        yesterday = yesterday_values[crypto]

        if today == yesterday:
            change = f"{today:.0f} | ➖"
        else:
            percentage_change = ((today - yesterday) / yesterday) * 100
            change = f"{yesterday:.0f} ➡️ {today:.0f} | {percentage_change:+.2f}%"

        msg += f"{crypto} | {change}\n"
    
    today_values = data.iloc[-1][LIST]
    total_interest = today_values.sum()
    proportions = {crypto: (value / total_interest) * 100 for crypto, value in today_values.items()}
    proportion_text = " | ".join([f"{crypto} {prop:.2f}%" for crypto, prop in proportions.items()])
    msg += f"\n🌍 *Dominance*\n{proportion_text}\n"

    return msg

def get_google_trends():
    data = get_data()
    msg = generate_message(data)
    return msg

