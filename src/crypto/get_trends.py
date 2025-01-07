from .get_greed_fear_index import get_greed_fear_index
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
from datetime import datetime, timedelta
import random
import time

CRYPTO_LIST = ['Bitcoin', 'Ethereum', 'Solana', 'Binance', "Doge"]

def get_data():
    pytrends = TrendReq()
    timeframe = 'today 1-m'
    pytrends.build_payload(CRYPTO_LIST, timeframe=timeframe)

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

def get_trends():
    trends_data = get_data()
    normalized_trends = trends_data[CRYPTO_LIST].apply(lambda x: (x / x.max()) * 100, axis=0)

    raw_today_values = trends_data[CRYPTO_LIST].iloc[-1]
    today_values = normalized_trends.iloc[-1]
    yesterday_values = normalized_trends.iloc[-2]
    last_30_days_values = normalized_trends.iloc[0]

    shares = {crypto: (value / raw_today_values.sum()) * 100 for crypto, value in raw_today_values.items()}

    msg = f"🔍 *Trending Crypto Searches*  ({get_greed_fear_index()})\n"
    msg += "```\n"
    msg += f"{'Crypto':<15}{'Search Share':<15}{'Yesterday':<16}{'Last 30 Days':<15}\n"
    msg += "-" * 77 + "\n"

    for crypto in CRYPTO_LIST:
        share = shares[crypto]

        today = today_values[crypto]
        yesterday = yesterday_values[crypto]
        yesterday_change = ((today - yesterday) / yesterday) * 100
        last_30_days = last_30_days_values[crypto]
        last_30_days_change = ((today - last_30_days) / last_30_days) * 100

        msg += f"{crypto:<10}{share:>10.2f}%{yesterday_change:>15.2f}%{last_30_days_change:>15.2f}%\n"

    msg += "```"
    return msg

