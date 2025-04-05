import pandas as pd
import sqlite3
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'test_data', 'inventory_monitoring.csv')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'inventory.db')

def run():
    df = pd.read_csv(DATA_PATH)
    df['Reorder_Needed'] = df['Stock Levels'] < df['Reorder Point']
    reorder_items = df[df['Reorder_Needed']]
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('inventory_status', conn, if_exists='replace', index=False)
    conn.close()
    return reorder_items.to_dict(orient='records')
