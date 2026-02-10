import sys

from setup_database import DB_CONFIG

sys.path.append("src")

from db_manager import DBManager
from data_fetcher import YahooFinanceDataFetcher
from data_loader import DataLoader

import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# DB_CONFIG = {
#     'host': os.getenv("DB_HOST"),
#     'user': os.getenv("DB_USER"),
#     'password': os.getenv("DB_PASSWORD"),
#     'database': os.getenv("DB_NAME"),
#     'port': os.getenv("DB_PORT")
# }

def main():
    db_manager = DBManager(DB_CONFIG)
    fetcher = YahooFinanceDataFetcher()
    loader = DataLoader(db_manager)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=5*365)

    print("=" * 60)
    print("QUANT ALPHA RESEARCH - DATA DOWNLOAD PIPELINE")
    print("=" * 60)

    # Get S&P 500 companies
    companies = fetcher.get_sp500_tickers()
    print(f"{len(companies)} companies downloaded")

    # Load companies metadata
    loader.load_securities(companies)

    # Download price data -- for now 10 stocks
    tickers = [c['ticker'] for c in companies][:10]
    print(f"Fetched {len(tickers)} tickers: {', '.join(tickers)}")

    all_price_data = []
    for i, ticker in enumerate(tickers, 1):
        try:
            df = fetcher.get_historical_prices(
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )

            if df is not None and not df.empty:
                print(f"Got {len(df)} rows for {ticker}")
                all_price_data.append(df)
            else:
                print(f"No rows for {ticker}")
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    if all_price_data:
        price_data = pd.concat(all_price_data, ignore_index=True)
        loader.load_daily_prices(price_data)

    index_data = fetcher.get_index_data(
        '^GSPC',
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

    if index_data is not None:
        loader.load_market_data(index_data)

if __name__ == "__main__":
    main()