import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'test_data', 'pricing_optimization.csv')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'inventory.db')

def run():
    df = pd.read_csv(DATA_PATH)
    base_date = datetime(2025, 1, 1)
    df['Date'] = [base_date + timedelta(days=i) for i in range(len(df))]
    df['Optimized_Price'] = df.apply(lambda row: row['Price'] * 0.95 if row['Competitor Prices'] < row['Price'] else row['Price'], axis=1)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('pricing_status', conn, if_exists='replace', index=False)
    conn.close()
    summary = df[['Product ID', 'Store ID', 'Price', 'Optimized_Price', 'Date']]
    return summary.to_dict(orient='records')
