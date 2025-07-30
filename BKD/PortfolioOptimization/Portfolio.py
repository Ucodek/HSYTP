import pandas as pd
# from pandas_datareader import data as pdr
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


from Optimizer import Optimizer
from ABD_RFR import get_tb3ms_value
from ABC import ABC_Model

class Portfolio:

    def __init__(self, stock_market) -> None:
        self.getStockNames(stock_market)

    def getStockNames(self, stock_market):
        try:
            if stock_market.lower() in ['nasdaq', 'nasdaq100', 'nasdaq-100']:
                url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
                tables = pd.read_html(url)
                # Doğru tabloyu kontrol et
                for table in tables:
                    if 'Symbol' in table.columns:
                        self.stocks = table['Symbol'].tolist()
                        break
                if self.stocks:
                    print("NASDAQ-100 Hisse Sembolleri:")
                    print(self.stocks)
                else:
                    print("NASDAQ-100 hisse listesi bulunamadı. Tabloları kontrol edin.")
                self.currency = "$"
                self.stock_market = "NASDAQ100"
                self.index_name = "^NDX"

            elif stock_market.lower() in ['bist100', 'bist-100', 'bist']:
                url = 'https://tr.wikipedia.org/wiki/Borsa_%C4%B0stanbul%27da_i%C5%9Flem_g%C3%B6ren_%C5%9Firketler_listesi'
                tables = pd.read_html(url)
                for table in tables:
                    if 'Kod' in table.columns:
                        self.stocks = (table['Kod'] + '.IS').tolist()
                        break
                if self.stocks:
                    print("BIST 100 Hisse Sembolleri:")
                    print(self.stocks)
                else:
                    print("BIST-100 Hisse listesi bulunamadı. Tabloları kontrol edin.")
                self.currency = "TL"
                self.stock_market = "BIST100"
                self.index_name = 'XU100.IS'

            else:
                print("Geçerli bir borsa ismi giriniz: 'nasdaq', 'nasdaq100', 'bist100'")
        except Exception as e:
            print(f"Hata oluştu: {e}")

    def createDataset(self, stocks, start, end):
        # end = start + timedelta(days=days)
        stockData = yf.download(stocks, start=start, end=end)['Close']
        if stockData.isna().sum().sum() > 0:
            stockData.fillna(method='ffill', inplace=True)
            stockData.dropna(axis=1, inplace=True)  # NaN içeren sütunları çıkar
        return stockData

    def get_previous_dates(self, date, train_days):
        # if date.day != 1:
        #     date.replace(day=1)
        start_date = date - timedelta(days=train_days)
        end_date = date - timedelta(days=1)
        return start_date, end_date
    
    def getRFR(self, date): # calculate and return risk free rate
        if self.stock_market == 'NASDAQ100':
            rfr = float(get_tb3ms_value(date.year, date.month)) / 252
        elif self.stock_market == 'BIST100':
            rfr = 50.0 / 252
        return rfr

    def trainPortfolio(self, date, train_days, opt_type, numberOfStock, evaNum=None, limit=None, P=None, MR=None, fitnessFun=None):
        # dates = all_dates[start : end]
        start_date, end_date = self.get_previous_dates(date, train_days)
        prices = self.createDataset(self.stocks, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        dates = prices.index.unique().sort_values()
        returns = pd.DataFrame(index=dates[1:])
        stocks = prices.columns
        # print(stocks)
        for stock in stocks:
            current_returns = prices[stock].pct_change()
            returns[stock] = current_returns.iloc[1:] * 100

        mean_return = returns.mean()
        cov = returns.cov()

        opt = Optimizer(mean_return=mean_return, cov=cov)

        if opt_type == 1:
            self.weights = opt.min_variance_optimizer()
            opt_method = 'min variance optimization'

        elif opt_type == 2:
            rfr = self.getRFR(start_date)
            self.weights = opt.sharpe_ratio_optimizer(rfr)
            opt_method = 'sharpe-raito optimization'

        elif opt_type == 3:
            rfr = self.getRFR(start_date)
            self.weights = opt.monte_carlo_optimizer(N=10000, risk_free_rate=rfr)
            opt_method = 'monte carlo optimization'

        elif opt_type == 4:
            rfr = self.getRFR(start_date)
            abc = ABC_Model(evaluationNumber=evaNum, limit=limit, P=P, MR=MR)
            # abc.fit(mean_return, cov, 'sharpe-ratio', rfr)
            abc.fit(mean_return, cov, fitnessFun, rfr)
            self.weights = abc.net
            opt_method = 'ABC optimization'

        # En yüksek ağırlığa sahip ilk 10 stoğu seç
        top_indices = np.argsort(self.weights)[-numberOfStock:]
        self.weights = self.weights[top_indices]
        self.stocks = np.array(stocks)[top_indices]

        # Ağırlıkları normalize et
        self.weights = self.weights / np.sum(self.weights)

        result = {}
        # result['opt_method'] = opt_method
        result['weights'] = {}
        result['weights(%)'] = {}
        result['weights'] = {stock: weight for stock, weight in zip(self.stocks, self.weights)}
        result['weights(%)'] = {stock: np.round(weight * 100, 2) for stock, weight in zip(self.stocks, self.weights) if np.round(weight * 100, 2) != 0}

        return result
    
    
    

    

