import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

class TimeSeriesStrategy:
    def __init__(self, portfolio, start_date, model, train_days):
        self.portfolio = portfolio
        self.start_date = start_date
        self.df = None
        self.T = 10
        self.preprocess = True
        if model == 'RF':
            self.preprocess = False

        self.models = {
            'RF': RandomForestClassifier(class_weight='balanced',random_state=42),
            'LR': LogisticRegression(class_weight='balanced'),
            'SVM': SVC(class_weight='balanced')
        }
        self.model = self.models.get(model, RandomForestClassifier())  # Varsayılan model: RandomForestClassifier
        self.train_days = train_days

    def create_dataset(self, stocks, start, end):
        try:
            stock_data = yf.download(stocks, start=start, end=end)['Close']
            if stock_data.isna().sum().sum() > 0:
                print("Eksik veri tespit edildi. Eksik veriler dolduruluyor...")
                stock_data.fillna(method='ffill', inplace=True)
                stock_data.dropna(axis=1, inplace=True)
            return stock_data
        except Exception as e:
            print(f"Veri çekme sırasında hata oluştu: {e}")
            return pd.DataFrame()

    def prepare_data(self):
        start_date_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
        start = (start_date_dt - timedelta(days=self.train_days)).strftime('%Y-%m-%d')
        end = (start_date_dt + pd.DateOffset(months=1)).strftime('%Y-%m-%d')
        today = datetime.today().date()
        end = end if datetime.strptime(end, '%Y-%m-%d').date() <= today else today.strftime('%Y-%m-%d')

        self.df = self.create_dataset(list(self.portfolio.keys()), start, end)

        if self.df.empty:
            print("Veri çekilemedi. Lütfen tarihleri ve sembolleri kontrol edin.")
            return

        for stock in self.portfolio.keys():
            self.df[f'{stock}_LogPrice'] = np.log(self.df[stock])
            self.df[f'{stock}_Return'] = self.df[f'{stock}_LogPrice'].diff()

    def generate_signals(self):
        Ntest = len(self.df[self.df.index >= self.start_date])

        for stock in self.portfolio.keys():
            series = self.df[f'{stock}_Return'].to_numpy()[1:]

            # X ve Y oluşturulması
            X = []
            Y = []

            for t in range(len(series) - self.T):
                X.append(series[t:t + self.T])
                # Pozitif getiri: 1 (Al), Negatif getiri: 0 (Sat)
                Y.append(1 if series[t + self.T] > 0 else 0)

            X = np.array(X).reshape(-1, self.T)
            Y = np.array(Y)

            X_train, Y_train = X[:-Ntest], Y[:-Ntest]
            X_test = X[-Ntest:]

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            # Model eğitimi ve tahmin
            self.model.fit(X_train, Y_train)
            predictions = self.model.predict(X_test)

            # Sinyal oluşturulması
            # Train kümesinin son elemanının sinyalini doğrudan hesapla
            train_last_signal = 1 if series[len(series) - Ntest - 1] > 0 else 0
            self.df.loc[self.df.index[len(X_train) - 1], f'{stock}_Signal'] = train_last_signal
            self.df.loc[self.df.index[-Ntest:], f'{stock}_Signal'] = predictions
            self.df[f'{stock}_PrevSignal'] = self.df[f'{stock}_Signal'].shift(1)
            self.df[f'{stock}_Buy'] = (self.df[f'{stock}_PrevSignal'] == 0) & (self.df[f'{stock}_Signal'] == 1)
            self.df[f'{stock}_Sell'] = (self.df[f'{stock}_PrevSignal'] == 1) & (self.df[f'{stock}_Signal'] == 0)

    def backtest(self):
        self.prepare_data()
        self.generate_signals()

        is_invested = {stock: False for stock in self.portfolio. keys()}
        new_columns = {}

        def assign_is_invested(row, stock):
            if is_invested[stock]:
                if row[f'{stock}_Sell']:
                    is_invested[stock] = False
            else:
                if row[f'{stock}_Buy']:
                    is_invested[stock] = True
            return is_invested[stock]

        for stock in self.portfolio.keys():
            new_columns[f'{stock}_IsInvested'] = self.df.apply(lambda row: assign_is_invested(row, stock), axis=1)
            new_columns[f'{stock}_AlgoReturn'] = new_columns[f'{stock}_IsInvested'] * self.df[f'{stock}_Return']

        # Tüm yeni sütunları bir DataFrame olarak birleştirin
        new_columns_df = pd.DataFrame(new_columns, index=self.df.index)

        # Orijinal DataFrame ile yeni sütunları tek seferde birleştirin
        self.df = pd.concat([self.df, new_columns_df], axis=1)

        # Sadece test verileri üzerinde kar-zarar hesaplaması yapın
        test_df = self.df[self.df.index >= self.start_date]

        test_df['PortfolioReturn'] = sum(test_df[f'{stock}_AlgoReturn'] * weight for stock, weight in self.portfolio.items())
        total_return = (1 + test_df['PortfolioReturn']).prod() - 1

        result = {
            'start_date': self.start_date,
            'end_date': test_df.index[-1].strftime('%Y-%m-%d'),
            'portfolio_gain(%)': np.round(total_return * 100, 2)
        }

        return result


# # Kullanım örneği
# if __name__ == "__main__":
#     portfolio = {'THYAO.IS': 0.3, 'AKBNK.IS': 0.4, 'SASA.IS': 0.3}
#     start_date = '2024-11-01'

#     strategy = TimeSeriesStrategy(portfolio, start_date)
#     result = strategy.backtest()
#     print(result)
