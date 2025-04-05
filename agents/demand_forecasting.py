import pandas as pd
import sqlite3
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'test_data', 'demand_forecasting.csv')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'inventory.db')

def run():
    df = pd.read_csv(DATA_PATH)
    forecast = df.groupby('Product ID')['Sales Quantity'].mean().reset_index()
    forecast.rename(columns={'Sales Quantity': 'Forecasted Sales'}, inplace=True)
    conn = sqlite3.connect(DB_PATH)
    forecast.to_sql('demand_forecast', conn, if_exists='replace', index=False)
    conn.close()
    return forecast.to_dict(orient='records')
