import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


class Evaluate:
    def __init__(self, stock_market) -> None:
        if stock_market.lower() == 'nasdaq' or stock_market.lower() == 'nasdaq100' or stock_market.lower() == 'nasdaq-100':
            self.currency = "$"
            self.stock_market = "NASDAQ100"
            self.index_name = "^NDX"
            
        elif stock_market.lower() == 'bist100' or stock_market.lower() == 'bist-100' or stock_market.lower() == 'bist':
            self.currency = "TL"
            self.stock_market = "BIST100"
            self.index_name = 'XU100.IS'

    def createDataset(self, stocks, start, end):
        stockData = yf.download(stocks, start=start, end=end)['Close']
        if stockData.isna().sum().sum() > 0:
            stockData.fillna(method='ffill', inplace=True)
            stockData.dropna(axis=1, inplace=True)  # NaN içeren sütunları çıkar
        return stockData
    
    def percentOfGain(self, x1, x2):
        return (x2 - x1) * 100 / x1

    def testPortfolio(self, date, days, buyWeights, buyStocks, budget = 100):
        start_date = date
        end_date = date + timedelta(days=days)
        stock_market_prices = self.createDataset(self.index_name, start=start_date, end=end_date)
        stock_market_start_price = stock_market_prices.iloc[0]
        stock_market_end_price = stock_market_prices.iloc[-1]
        stock_market_gain_percentage = self.percentOfGain(stock_market_start_price, stock_market_end_price)

        portfolio_prices = self.createDataset(buyStocks, start=start_date, end=end_date)
        stock_budgets = budget * buyWeights
        amounts = stock_budgets / portfolio_prices.iloc[0]
        final_budget = np.sum(amounts * portfolio_prices.iloc[-1])

        result = {}
        result['start-date']=start_date
        result['end-date']=end_date
        result['budget'] = budget
        result['final-budget'] = final_budget
        result['currency'] = self.currency
        result['stock-market'] = self.stock_market
        result['index'] = self.index_name
        result['stock-market-gain(%)'] = np.round(stock_market_gain_percentage,2)
        result['portfolio-gain(%)'] = np.round(self.percentOfGain(budget, final_budget),2)
        result['detail'] = {}
        
        cost = amounts * portfolio_prices.iloc[0]
        final = amounts * portfolio_prices.iloc[-1]
        kar = final - cost

        for m, i, j, k, l in zip(buyStocks, amounts, cost, final, kar):
            if i > 0:
                result['detail'][m] = {
                    'amount': np.round(i,2),
                    'cost' : np.round(j,2),
                    'final' : np.round(k,2),
                    'gain': np.round(l,2)
                }
            else: continue
        return result


