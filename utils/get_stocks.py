import os 
import pandas as pd

DATA_PATH = os.getenv('STOCK_DATA_PATH')

def get_all_tickers():
    return pd.read_pickle(DATA_PATH + '/all_stock.pkl')
