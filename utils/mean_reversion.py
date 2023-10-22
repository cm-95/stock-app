from utils import stock_data as sd
import pandas as pd


class MeanReversion:
    def __init__(self, short_sma=20, long_sma=60):
        self.stock_data = sd.StockData().get_stock_data()
        self.short_mavg = self.stock_data.rolling(window=short_sma, center=False).mean()
        self.long_mavg = self.stock_data.rolling(window=long_sma, center=False).mean()
        self.mavg_spread = (self.short_mavg - self.long_mavg) / self.long_mavg
        self.last_month_data = self.mavg_spread.tail(20)
        # check if short mavg is above long mavg
        self.cols = (self.last_month_data > 0).all()
        self.undv_stocks = self.mavg_spread[self.cols[self.cols].index]
        # Momentum from 20 trading days ago
        self.m_undv = self.stock_data.pct_change(20)
        self.last_day_m = self.m_undv.tail(20)
        self.undv_stocks = self.undv_stocks[self.cols[self.cols].index]
        self.ranked_stocks = self.rank_stocks()

    def rank_stocks(self):
        last_week_m = pd.DataFrame(
            self.m_undv.tail(5).sum().reset_index().values,
            columns=["Ticker", "M_Indicator"],
        )
        last_week_sma = pd.DataFrame(
            self.undv_stocks.tail(20).sum().reset_index().values,
            columns=["Ticker", "SMA_Abs_Diff"],
        )

        df_vol = pd.DataFrame(
            self.stock_data.tail(400)
            .rolling(window=20)
            .std()
            .sum()
            .reset_index()
            .values,
            columns=["Ticker", "Vol"],
        )

        last_week_m["Rank_M"] = last_week_m.M_Indicator.rank()
        last_week_sma["Rank_SMA"] = last_week_sma.SMA_Abs_Diff.rank()
        df_vol["Rank_Vol"] = df_vol.Vol.rank(ascending=False)

        last_week = last_week_m.merge(last_week_sma, on="Ticker", how="left").dropna()
        last_week = last_week.merge(df_vol, on="Ticker", how="left").dropna()
        last_week["Overall_Rank"] = (
            last_week.Rank_M + last_week.Rank_SMA + last_week.Rank_Vol
        )
        # last_week['Overall_Rank'] = last_week.Rank_SMA

        return last_week.sort_values("Overall_Rank").reset_index(drop=True)

    def show_top_stocks(self):
        top_stocks = list(self.ranked_stocks.head(20).Ticker)
        top_stocks_p = self.stock_data[top_stocks]

        stock_dict = {}

        for stock in top_stocks:
            p = top_stocks_p[[stock]]
            s_sma = self.short_mavg[[stock]]
            l_sma = self.long_mavg[[stock]]

            sub_df = p.join(s_sma, lsuffix="_PRICE", rsuffix="_S_SMA")

            sub_df = sub_df.join(l_sma).rename(columns={stock: f"{stock}_L_SMA"})

            sub_df.tail(365).plot(
                figsize=(25, 10), title=stock, fontsize=15
            ).title.set_size(30).show()
