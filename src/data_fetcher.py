import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class YahooFinanceDataFetcher:
    def __init__(self):
        pass

    def get_sp500_tickers(self):
        """Fetches S&P 500 tickers from yahoo finance"""
        # Download S&P 500 list
        url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv'
        sp500 = pd.read_csv(url)

        # Also get company info
        companies = []
        for _, row in sp500.iterrows():
            companies.append({
                'ticker': row['Symbol'].replace('.', '-'),
                'company_name': row['Security'],
                'sector': row['GICS Sector'],
                'industry': row['GICS Sub-Industry'],
            })
        return companies

    def get_historical_prices(self, ticker, start_date, end_date):
        """Fetches historical prices for a single ticker"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)

            if df.empty:
                print("No data for {}".format(ticker))
                return None

            # Reset index to get date as column
            df.reset_index(inplace=True)
            df['ticker'] = ticker

            # Rename columns to match schema
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
            })

            # Calculate adjusted close (yfinance's Close is already adjusted)
            df['adj_close'] = df['close']

            return df[['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close']]

        except Exception as e:
            print(f"Error fetching historical prices for {ticker}: {e}")
            return None


    def get_index_data(self, index_symbol, start_date, end_date):
        """Fetches index data"""

        try:
            index = yf.Ticker(index_symbol)
            df = index.history(start=start_date, end=end_date)
            df.reset_index(inplace=True)
            df['index_name'] = index_symbol

            df = df.rename(columns={
                'Date': 'date',
                'Close': 'close',
                'Volume': 'volume',
            })

            return df[['date', 'index_name', 'close', 'volume']]

        except Exception as e:
            print(f"Error fetching index data for {index_symbol}: {e}")
            return None
