from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from Portfolio import Portfolio
from Evaluate import Evaluate
from TFS import TrendFollowingStrategy
from TimeSeriesV2 import TimeSeriesStrategy

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Portfolio Optimization created by Dr. Bilge Kagan Dedeturk."

@app.route('/trainPortfolio', methods=['POST'])
def train_portfolio():
    try:
        data = request.get_json()
        stock_market = data['stock_market']
        date = pd.to_datetime(data['date'])
        train_days = data['train_days']
        opt_type = data['opt_type']
        number_of_stock = data.get('numberOfStock', 10)

        portfolio = Portfolio(stock_market=stock_market)

        if opt_type == 4:
            evaNum = data.get('evaNum', 200000)
            limit = data.get('limit', 20)
            P = data.get('P', 100)
            MR = data.get('MR', 0.1)
            fitnessFun = data.get('fun', 'dengeli')
            weights = portfolio.trainPortfolio(date=date, train_days=train_days, opt_type=opt_type, numberOfStock=number_of_stock, evaNum=evaNum, limit=limit, P=P, MR=MR, fitnessFun=fitnessFun)
        else:
            weights = portfolio.trainPortfolio(date=date, train_days=train_days, opt_type=opt_type, numberOfStock=number_of_stock)
        return jsonify(weights)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/evaluatePortfolio', methods=['POST'])
def evaluatePortfolio():
    try:
        data = request.get_json()

        # JSON verisinden gerekli bilgileri almak için
        stock_market = data.get('stock_market')
        date = pd.to_datetime(data.get('date'))
        days = data.get('days')
        stock_weights = data.get('stock-weights')

        # Anahtar ve değerleri listeye dönüştürmek için
        stocks = list(stock_weights.keys())
        weights = np.array(list(stock_weights.values()))

        evaluate = Evaluate(stock_market=stock_market)
        result = evaluate.testPortfolio(date=date, days=days, buyWeights=weights, buyStocks=stocks, budget=1000)

        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

@app.route('/tfs', methods=['POST'])
def tfs():
    try:
        data = request.get_json()

        # JSON verisinden gerekli bilgileri almak için
        # stock_market = data.get('stock_market')
        date = data.get('date')
        # days = data.get('days')
        portfolio = data.get('portfolio')

        evaluate = TrendFollowingStrategy(portfolio, date)
        result = evaluate.backtest()

        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/time-series', methods=['POST'])
def timeSeries():
    try:
        data = request.get_json()

        # JSON verisinden gerekli bilgileri almak için
        # stock_market = data.get('stock_market')
        date = data.get('date')
        train_days = data.get('train-days', 120)
        model = data.get('model', 'RF') # RF, LR, SVM
        # days = data.get('days')
        portfolio = data.get('portfolio')

        evaluate = TimeSeriesStrategy(portfolio, date, model, train_days)
        result = evaluate.backtest()

        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(port=5050, debug=True)




