import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

class TrendFollowingStrategy:
    def __init__(self, portfolio, start_date):
        self.portfolio = portfolio
        self.start_date = start_date
        self.df = None

    def createDataset(self, stocks, start, end):
        stockData = yf.download(stocks, start=start, end=end)['Close']
        if stockData.isna().sum().sum() > 0:
            print("Eksik veri tespit edildi. Eksik veriler dolduruluyor...")
            stockData.fillna(method='ffill', inplace=True)
            stockData.dropna(axis=1, inplace=True) # NaN içeren sütunları çıkar
        return stockData

    def backtest(self):
        today = datetime.today().date()
        start_date_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
        start = (start_date_dt - timedelta(days=30)).strftime('%Y-%m-%d')
        end = (start_date_dt + pd.DateOffset(months=1)).strftime('%Y-%m-%d')
        end = end if datetime.strptime(end, '%Y-%m-%d').date() <= today else today.strftime('%Y-%m-%d')

        # Veriyi çekme (30 gün öncesinden)
        self.df = self.createDataset(list(self.portfolio.keys()), start, end)

        if self.df.empty:
            print("Veri çekilemedi. Lütfen tarihleri ve sembolleri kontrol edin.")
            return

        # Her hisse için TFS uygulama
        for stock in self.portfolio.keys():
            self.df[f'{stock}_Return'] = self.df[stock].pct_change()
            self.df[f'{stock}_SlowSMA'] = self.df[stock].rolling(30).mean()
            self.df[f'{stock}_FastSMA'] = self.df[stock].rolling(10).mean()
            self.df[f'{stock}_Signal'] = np.where(self.df[f'{stock}_FastSMA'] >= self.df[f'{stock}_SlowSMA'], 1, 0)
            self.df[f'{stock}_PrevSignal'] = self.df[f'{stock}_Signal'].shift(1)
            self.df[f'{stock}_Buy'] = (self.df[f'{stock}_PrevSignal'] == 0) & (self.df[f'{stock}_Signal'] == 1)
            self.df[f'{stock}_Sell'] = (self.df[f'{stock}_PrevSignal'] == 1) & (self.df[f'{stock}_Signal'] == 0)

        # SMA ve sinyaller hesaplandıktan sonra filtreleme
        self.df = self.df.loc[self.start_date:end]

        # Yatırım durumunu belirleme
        is_invested = {stock: False for stock in self.portfolio.keys()}

        def assign_is_invested(row, stock):
            if is_invested[stock] and row[f'{stock}_Sell']:
                is_invested[stock] = False
            if not is_invested[stock] and row[f'{stock}_Buy']:
                is_invested[stock] = True
            return is_invested[stock]

        for stock in self.portfolio.keys():
            self.df[f'{stock}_IsInvested'] = self.df.apply(lambda row: assign_is_invested(row, stock), axis=1)
            self.df[f'{stock}_AlgoReturn'] = self.df[f'{stock}_IsInvested'] * self.df[f'{stock}_Return']

        # Portföy genel getiri hesaplama
        self.df['PortfolioReturn'] = sum(self.df[f'{stock}_AlgoReturn'] * weight for stock, weight in self.portfolio.items())

        # Toplam portföy getirisi
        total_return = (1 + self.df['PortfolioReturn']).prod() - 1
        # print(f"Portföyün toplam getirisi: %{total_return * 100:.2f}")

        result = {}
        result['start-date']=self.start_date
        result['end-date']=end
        result['portfolio-gain(%)'] = np.round(total_return * 100, 2)
        return result

# # Kullanım örneği
# if __name__ == "__main__":
#     portfolio = {'THYAO.IS': 0.3, 'AKBNK.IS': 0.4, 'SASA.IS': 0.3}
#     start_date = '2024-11-01'

#     strategy = TrendFollowingStrategy(portfolio, start_date)
#     strategy.backtest()
