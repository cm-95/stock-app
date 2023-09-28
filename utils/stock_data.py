from pandas_datareader import data as pdr
from datetime import datetime, date, timedelta
import yfinance as yfin
import os
import pandas as pd
import get_stocks


def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4:  # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate


class StockData:
    def __init__(self):
        self.DATA_PATH = os.getenv("STOCK_DATA_PATH")
        self.all_stock_data = self._load_all_stock_data()
        self.max_date = self._find_max_date()
        self.close_data = self._filter_close_data(self.all_stock_data)
        self.datetime_check = self._check_for_more_data_needed()
        self._update_close_data()
        self._save_close_data()

    @property
    def tickers(self):
        return list(get_stocks.get_all_tickers().Symbol)

    def get_stock_data(self):
        return self.close_data

    def _load_all_stock_data(self):
        return pd.read_pickle(self.DATA_PATH + "/all_data.pkl")

    def _find_max_date(self):
        return max(self.all_stock_data.index)

    def _filter_close_data(self, data):
        return data.loc[:, data.columns.get_level_values(0).isin({"Close"})].droplevel(
            0, axis=1
        )

    def _check_for_more_data_needed(self):
        return prev_weekday(datetime.today().date()) <= self.max_date.date()

    def _update_close_data(self):
        if not self.datetime_check:
            yfin.pdr_override()
            new_data = pdr.get_data_yahoo(
                self.tickers, start=self.max_date, end=datetime.today().date()
            )
            pd.concat([self.all_stock_data, new_data]).to_pickle(
                self.DATA_PATH + "/all_data.pkl"
            )
            new_data = self._filter_close_data(new_data)
            self.close_data = pd.concat([self.close_data, new_data])

    def _save_close_data(self):
        self.close_data.to_pickle(self.DATA_PATH + "/close_data.pkl")


sd = StockData()

sd.get_stock_data()
print()
