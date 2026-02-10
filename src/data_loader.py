from db_manager import DBManager

import pandas as pd
from datetime import datetime

class DataLoader:
    def __init__(self, db_manager):
        self.db = db_manager

    def load_securities(self, companies):
        """Loads securities from metadata"""
        query = """
            INSERT INTO securities (ticker, company_name, sector, industry, is_active)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                updated_at = CURRENT_TIMESTAMP
        """

        data = [
            (c['ticker'], c['company_name'], c['sector'], c['industry'], True)
            for c in companies
        ]

        self.db.execute_many(query, data)
        print(f"Loaded {len(companies)} securities")

    def load_daily_prices(self, df):
        """Loads daily prices data from DataFrame"""
        query = """
            INSERT INTO daily_prices (ticker, date, open, high, low, close, volume, adj_close)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, date) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                adj_close = EXCLUDED.adj_close
        """

        # Convert DataFrame to list of tuples
        data = [
            (row['ticker'], row['date'], row['open'], row['high'],
             row['low'], row['close'], row['volume'], row['adj_close'])
            for _, row in df.iterrows()
        ]

        self.db.execute_many(query, data)
        print(f"Loaded {len(df)} daily prices")

    def load_market_data(self, df):
        """Loads index/market data"""
        query = """
            INSERT INTO market_data (date, index_name, close, volume)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date, index_name) DO UPDATE SET
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """

        data = [
            (row['date'], row['index_name'], row['close'], row['volume'])
            for _, row in df.iterrows()
        ]

        self.db.execute_many(query, data)
        print(f"Loaded {len(df)} market data")
