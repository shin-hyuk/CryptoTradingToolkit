import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import pearsonr
from btc.get_distribution import get_data_since as get_distribution

def get_price(start_date):
    price_data_path = './src/trade/BINANCE_BTCUSDT, 1D.csv'
    price_df = pd.read_csv(price_data_path)
    price_df.rename(columns={'time': 'Date', 'close': 'Price'}, inplace=True)
    price_df['Date'] = pd.to_datetime(price_df['Date'], format='%Y-%m-%d')
    necessary_columns = ['Date', 'Price']
    price_df = price_df[necessary_columns]

    start_date = pd.to_datetime(start_date)
    price_df = price_df[price_df['Date'] >= start_date]
    price_df.reset_index(drop=True, inplace=True)

    return price_df


def test_holdings(start_date):

    price_df = get_price(start_date)
    distribution_df = get_distribution(start_date)

    periods = {
        '1_Week': 7,
        '1_Month': 30,
        '3_Months': 90,
        'Overall': None  # Overall doesn't filter data, uses everything
    }

    # Merge price and distribution data into combined_df
    price_df['Date'] = pd.to_datetime(price_df['Date'])
    distribution_df['Date'] = pd.to_datetime(distribution_df['Date'])

    combined_df = price_df.merge(distribution_df, on='Date', how='inner')
    
    # Calculate daily changes in holdings (distribution ranges) and price
    for column in distribution_df.columns:
        if column != 'Date':
            combined_df[f'{column}_Change'] = combined_df[column].diff()

    combined_df['Price_Change'] = combined_df['Price'].pct_change()

    # Define price behavior categories
    def categorize_price_change(change):
        if change > 0.01:
            return 'Up'
        elif change < -0.01:
            return 'Down'
        else:
            return 'Fluctuate'

    combined_df['Price_Behavior'] = combined_df['Price_Change'].apply(categorize_price_change)

    # Drop NaN values caused by diff() and pct_change()
    combined_df.dropna(inplace=True)

    # Prepare the final results
    behavior_results = []
    projected_results = []  # To store projections for future

    # Ensure 'Date' is sorted in ascending order for accurate filtering
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)

    for column in combined_df.columns:
        if column.endswith('_Change') and column != 'Price_Change':
            for period_name, period_days in periods.items():
                # Filter the data for the specific period (if not overall)
                if period_days is not None:
                    filtered_df = combined_df.tail(period_days)
                else:
                    filtered_df = combined_df  # Use the entire dataset for overall

                # Analyze Up and Fluctuate probabilities
                for direction, label in [(1, 'Increase'), (-1, 'Decrease')]:
                    subset = filtered_df[filtered_df[column] * direction > 0]
                    behavior_counts = subset['Price_Behavior'].value_counts(normalize=True)

                    # Append results for this period
                    behavior_results.append({
                        'Metric': column,
                        'Period': period_name,
                        'Direction': label,
                        'Up_Probability': behavior_counts.get('Up', 0),
                        'Fluctuate_Probability': behavior_counts.get('Fluctuate', 0)
                    })

                # Calculate projections for future price behavior (if Direction is Increase)
                if period_name != 'Overall':
                    up_probability = filtered_df['Price_Behavior'].value_counts(normalize=True).get('Up', 0)
                    projected_results.append({
                        'Metric': column,
                        'Period': period_name,
                        'Projected_Up_Probability': up_probability
                    })

    # Convert results into DataFrames
    behavior_df = pd.DataFrame(behavior_results)
    projections_df = pd.DataFrame(projected_results)

    # Save the DataFrames to CSV
    behavior_df.to_csv('behavior_results.csv', index=False)
    projections_df.to_csv('projected_results.csv', index=False)

    print("Behavior analysis complete. Results saved to 'behavior_results.csv' and 'projected_results.csv'.")
    return behavior_df, projections_df
