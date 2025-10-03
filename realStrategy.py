from backtesting import Backtest, Strategy
import pandas as pd
data = pd.read_csv(r"C:\Users\HP\OneDrive\Documents\icici_data.csv")
data['Open'] = pd.to_numeric(data['Open'], errors='coerce')
data['High'] = pd.to_numeric(data['High'], errors='coerce')
data['Low'] = pd.to_numeric(data['Low'], errors='coerce')
data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
data.dropna(inplace=True)
''' below 2 line code needed as it corrects format of dates needed by backtesting.py library'''
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
data.set_index('Date', inplace=True)

def bollinger_bands(series, period, stddev):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = sma + stddev * std
    lower = sma - stddev * std
    return upper, sma, lower

class strategy(Strategy):
    bb_period = 20
    bb_stddev = 2
    sma_period = 14

    def init(self):
        close = pd.Series(self.data.Close)
        self.upper, self.middle, self.lower = self.I(bollinger_bands, close, self.bb_period, self.bb_stddev)
        self.sma = self.I(lambda x: pd.Series(x).rolling(self.sma_period).mean(), close)

    def next(self):
        price = self.data.Close[-1]
        lookback = 10
        recent_low = min(self.data.Low[-lookback:])
        recent_high = max(self.data.High[-lookback:])
        if not self.position:
           if price <=self.lower[-1]:

            sl= recent_low * 0.99
            tp = price + (price - sl) * 2
            self.buy(sl=sl, tp=tp)

           elif price >=self.upper[-1]:

            sl = recent_high * 1.01
            tp = price - (sl - price) * 2

            self.sell(sl=sl, tp=tp)


        elif self.position:
            if self.position.is_long and price > (self.upper[-1]+self.sma[-1])/2:
                self.position.close()
            elif self.position.is_short and price < (self.lower[-1]+self.sma[-1])/2:
                self.position.close()

bt = Backtest(data, strategy, cash=500000, commission=.001)
results = bt.optimize(
    bb_period=range(10, 30, 5),
    bb_stddev=[1.5, 2.0, 2.5, 3.0],
    sma_period=range(5, 25, 5),
    maximize='Return [%]' )
print(results)

bt.plot()