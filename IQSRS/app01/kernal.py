import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import sys
import seaborn
from numpy import ndarray
from pandas import DataFrame, Series
from pandas.core.generic import NDFrame

from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from collections import deque
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
import os
import re
import pickle
import pysentiment as ps
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from gensim.models.word2vec import Word2Vec
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.cluster import KMeans
import random
import warnings
random.seed(114514)
warnings.filterwarnings("ignore")


class Parameter:
    val = 0
    mnval = 0
    mxval = 0
    step = 0

    def __init__(self, mnval=0, mxval=0, step=0):
        self.mnval = mnval
        self.mxval = mxval
        self.step = step

    def set(self, mnval, mxval, step=1):
        self.mnval = mnval
        self.mxval = mxval
        self.step = step

    def genint(self):
        self.val = np.random.random_integers(self.mnval / self.step, self.mxval / self.step) * self.step

    def genfloat(self):
        self.val = np.random(self.mnval / self.step, self.mxval / self.step) * self.step


class Result:
    startCash = 0
    Cash = 0
    Asset = 0
    Share = 0
    Return = 0
    Alpha = 0
    Sharpe = 0
    buypoint = []
    sellpoint = []

    def __init__(self):
        pass

    def cal(self, bar, BMbar, starttime, endtime):
        self.Return = (self.Asset - self.startCash) / self.startCash
        self.Alpha = self.alpha_beta(bar, BMbar, 0.03)[0]
        self.Sharpe = self.sharpeRatio(bar, BMbar, starttime, endtime)

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=0):
        pass

    def sharpeRatio(self, bar, BMbar, starttime, endtime):
        bar = bar[bar['Date'] > pd.to_datetime(starttime)]
        bar = bar[bar['Date'] < pd.to_datetime(endtime)]
        bar.index = range(len(bar))
        BMbar = BMbar[BMbar['Date'] > pd.to_datetime(starttime)]
        BMbar = BMbar[BMbar['Date'] < pd.to_datetime(endtime)]
        BMbar.index = range(len(BMbar))
        real_starttime = str(bar['Date'][0]).split(" 00:00:00")[0]
        real_endtime = str(bar['Date'][len(bar)-1]).split(" 00:00:00")[0]
        timedelta = dt.datetime.strptime(real_starttime, "%Y-%m-%d").date() - \
                    dt.datetime.strptime(real_endtime, "%Y-%m-%d").date()
        duringdays = timedelta.days
        expected_stock = (bar['Close'][len(bar)-1]/bar['Close'][0]) ** (365 / duringdays)
        expected_strate = (expected_stock - 1) * 100
        expected_market = (BMbar['Close'][len(BMbar)-1] / BMbar['Close'][0]) ** (365 / duringdays)
        expected_marate = (expected_market - 1) * 100
        risk = np.std(bar['Close'], ddof=1)
        sharpe_value = (expected_strate - expected_marate)/risk
        return sharpe_value

    def alpha_beta(self, stock_data, benchmark_data, rf=0):  # rf-无风险年利率
        data_len = len(stock_data)
        try:
            date_list = stock_data["Date"]
        except:
            date_list = list(stock_data.index)
        start_date = date_list[0]
        start_date = dt.datetime.strptime(str(start_date)[0:10], "%Y-%m-%d").date()
        end_date = date_list[data_len - 1]
        end_date = dt.datetime.strptime(str(end_date)[0:10], "%Y-%m-%d").date()
        date_years = (end_date - start_date).days / 365
        rf = rf ** (1 / date_years)
        seq = np.array(stock_data["Close"])
        seq_bench = np.array(benchmark_data["Close"])
        seq_return = seq[-1] / seq[0] - 1
        seq_bench_return = seq_bench[-1] / seq_bench[0] - 1
        seq_bench = seq_bench[1:] / seq_bench[0:-1] - 1
        seq = seq[1:] / seq[0:-1] - 1
        e_seq_bench = sum(seq_bench) / len(seq_bench)
        e_seq = sum(seq) / len(seq)
        cov = (seq_bench - e_seq_bench) * (seq - e_seq)
        cov = sum(cov) / len(cov)
        var = (seq_bench - e_seq_bench) ** 2
        var = sum(var) / len(var)
        beta_value = cov / var
        alpha_value = seq_return - rf - beta_value * seq_bench_return
        return (alpha_value, beta_value)

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=1):
        pass


class Stop_Price:
    def __init__(self):
        pass

    stop_profit = float('inf')
    stop_loss = -float('inf')

    def set_limit(self, stop_profit=float('inf'), stop_loss=-float('inf')):
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss
        return stop_profit, stop_loss


class Strategy(Result, Stop_Price, Parameter):
    pdata = pd.DataFrame()

    def __init__(self):
        pass

    def clear(self):
        self.Asset = self.startCash
        self.Cash = self.startCash
        self.Share = 0
        self.Alpha = 0
        self.Sharpe = 0
        self.Return = 0
        self.buypoint = []
        self.sellpoint = []
        self.pdata = pd.DataFrame()

    def setcash(self, Cash):
        self.startCash = self.Cash = self.Asset = Cash

    def sell(self, time, price, shares):
        # limit
        self.Cash += price * shares
        self.Share -= shares
        self.sellpoint.append([time, price])

    def buy(self, time, price, shares):
        # limit
        print("buy: ", time, shares, price)
        self.buyprice = price
        self.Cash -= price * shares
        self.Share += shares
        self.buypoint.append([time, price])

    def liquidate(self, time, price):
        self.Cash += self.Share * price
        print("sell:", time, self.Share, price, self.Cash)
        self.Share = 0
        self.sellpoint.append([time, price])

    def checklimit(self, time, price):
        stop_profit = self.stop_profit
        stop_loss = self.stop_loss
        buyprice = self.buyprice
        if (price - buyprice) / buyprice > stop_profit or (price - buyprice) / buyprice < stop_loss:
            self.liquidate(time, price)
            return 1
        else:
            return 0

    def stop_limit(self, time, price):
        self.Cash += self.Share * price
        print("limit：", time, self.Share, price, self.Cash)
        self.Share = 0
        self.sellpoint.append([time, price])

    def test(self, starttime, endtime):
        pass

    def train(self, token, starttime, endtime, times):
        pass

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=1):
        pass


class _MACD(Strategy):
    slen = 0  # best parameter
    llen = 0
    bestAsset = 0
    _slen = Parameter()  # train parameter
    _llen = Parameter()
    istrainready = 0

    def __init__(self):
        pass

    def setlen(self, slen=20, llen=60):
        self.slen = slen
        self.llen = llen

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=0):
        self.cal(bar, BMbar, starttime, endtime)
        self.data = yf.Ticker(token)
        print('-------------------RESULT----------------------')
        print("Stock:", token)
        print("startCash:", self.startCash)
        print("Asset:", round(self.Asset, 2))
        print("Cash:", round(self.Cash, 2))
        print("Share:", round(self.Share, 2))
        print("Alpha:", round(self.Alpha, 2))
        print("Sharpe:", round(self.Sharpe, 2))
        print("buy:", self.buypoint)
        print("sell:", self.sellpoint)
        print("Return: {:.2%}".format(self.Return))
        print('-----------------------------------------------')
        bar = bar[pd.to_datetime(starttime) <= bar['Date']]
        bar = bar[bar['Date'] <= pd.to_datetime(endtime)]
        self.pdata = self.pdata[pd.to_datetime(starttime) <= self.pdata['Date']]
        self.pdata = self.pdata[self.pdata['Date'] <= pd.to_datetime(endtime)]
        plt.clf()
        plt.subplot(2, 1, 1)
        plt.plot(bar['Date'], bar['Close'])
        plt.plot(self.pdata['Date'], self.pdata['SMA'], label='SMA')
        plt.plot(self.pdata['Date'], self.pdata['LMA'], label='LMA')
        plt.legend()
        plt.ylabel("Price(USD)")
        plt.subplot(2, 1, 2)
        plt.ylabel("Asset(USD)")
        plt.plot(bar['Date'], self.pdata['Asset'])
        plt.tight_layout()
        if saveimg:
            plt.savefig('./Result/' + token + dt.datetime.now().strftime('%H%M%S'))

    def test(self, bar, starttime, endtime, istrain=0):
        self.clear()
        if istrain:
            llen = self._llen.val
            slen = self._slen.val
        else:
            llen = self.llen
            slen = self.slen
        for i in range(llen + 1, len(bar)):
            if not (pd.to_datetime(starttime) <= bar.Date[i] <= pd.to_datetime(endtime)): continue
            self.pdata.loc[i, ['Date']] = bar.loc[i, ['Date']]
            sma_pre = bar.Close[i - slen:i].mean()
            sma_now = bar.Close[i - slen + 1:i + 1].mean()
            lma_pre = bar.Close[i - llen:i].mean()
            lma_now = bar.Close[i - llen + 1:i + 1].mean()
            self.pdata.loc[i, ['SMA']] = sma_now  # record , get ready for plot
            self.pdata.loc[i, ['LMA']] = lma_now
            if self.Share == 0:
                if sma_pre < lma_pre and sma_now > lma_now:
                    self.buy(bar.Date[i], bar.Close[i], self.Cash / bar.Close[i])  # Buy with all cash
            else:
                self.Asset += self.Share * (bar.Close[i] - bar.Close[i - 1])  ##
                if self.checklimit(bar.Date[i], bar.Close[i]) == 0:
                    if sma_pre > lma_pre and sma_now < lma_now:
                        self.liquidate(bar.Date[i], bar.Close[i])  # Sell all shares
            self.pdata.loc[i, ['Asset']] = self.Asset
        if istrain and self.Asset > self.bestAsset:
            self.bestAsset = self.Asset
            self.llen = self._llen.val
            self.slen = self._slen.val

    def traininit(self, _slen, _llen):
        self._slen = _slen
        self._llen = _llen
        self.istrainready = 1
        self.bestAsset = -np.inf

    def train(self, bar, starttime, endtime, times):
        if self.istrainready != 1:
            print('Parameters\' range is not set.')
            sys.exit(0)
            return
        for i in range(times):
            self._slen.genint()
            self._llen.genint()
            while self._slen.val == self._llen.val:
                self._slen.genint()
                self._llen.genint()
            if self._slen.val > self._llen.val:
                self._slen.val, self._llen.val = self._llen.val, self._slen.val
            self.test(bar, starttime, endtime, 1)


class _RBreaker(Strategy):
    ylen = 0  # best parameter
    mlen = 0
    bestAsset = 0
    _ylen = Parameter()  # train parameter
    _mlen = Parameter()
    istrainready = 0

    def __init__(self):
        pass

    def setlen(self, ylen=1, mlen=3):
        self.ylen = ylen
        self.mlen = mlen

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=1):
        self.cal(bar, BMbar, starttime, endtime)
        self.data = yf.Ticker(token)
        print('-------------------RESULT----------------------')
        print("Stock:", token)
        print("startCash:", self.startCash)
        print("Asset:", round(self.Asset, 2))
        print("Cash:", round(self.Cash, 2))
        print("Share:", round(self.Share, 2))
        print("Alpha:", round(self.Alpha, 2))
        print("Sharpe:", round(self.Sharpe, 2))
        print("buy:", self.buypoint)
        print("sell:", self.sellpoint)
        print("Return: {:.2%}".format(self.Return))
        print('-----------------------------------------------')
        bar = bar[pd.to_datetime(starttime) <= bar['Date']]
        bar = bar[bar['Date'] <= pd.to_datetime(endtime)]
        self.pdata = self.pdata[pd.to_datetime(starttime) <= self.pdata['Date']]
        self.pdata = self.pdata[self.pdata['Date'] <= pd.to_datetime(endtime)]
        plt.clf()
        plt.subplot(2, 1, 1)
        plt.plot(bar['Date'], bar['Close'])
        plt.plot(self.pdata['Date'], self.pdata['Pivot'])
        plt.plot(self.pdata['Date'], self.pdata['Break'])
        label = ["Close", "Pivot", "Break"]
        plt.legend(label)
        plt.ylabel("Price(USD)")
        plt.subplot(2, 1, 2)
        plt.ylabel("Asset(USD)")
        plt.plot(bar['Date'], self.pdata['Asset'])
        plt.tight_layout()
        if saveimg:
            plt.savefig('./Result/' + token + dt.datetime.now().strftime('%H%M%S'))

    def test(self, bar, starttime, endtime, istrain=0):
        self.clear()
        if istrain:
            ylen = self._ylen.val
            mlen = self._mlen.val
        else:
            ylen = self.ylen
            mlen = self.mlen
        for i in range(mlen + 1, len(bar)):
            if not (pd.to_datetime(starttime) <= bar.Date[i] <= pd.to_datetime(endtime)): continue
            self.pdata.loc[i, ['Date']] = bar.loc[i, ['Date']]
            # cal Pivot
            mhigh = bar.High[i - mlen:i].mean()
            mlow = bar.Low[i - mlen:i].mean()
            mclose = bar.Close[i - mlen:i].mean()
            pivot = (mhigh + mlow + mclose) / 3
            bBreak = mhigh + 2 * (pivot - mlow)
            sSetup = pivot + (mhigh - mlow)
            sEnter = 2 * pivot - mlow
            bEnter = 2 * pivot - mhigh
            bSetup = pivot - (mhigh - mlow)
            sBreak = pivot - 2 * (mhigh - mlow)
            p = bar.Close[i]
            yhigh = bar.High[i - ylen:i].mean()
            ylow = bar.Low[i - ylen:i].mean()
            self.pdata.loc[i, ['Pivot']] = pivot  # record , get ready for plot
            self.pdata.loc[i, ['Close']] = mclose
            self.pdata.loc[i, ['Break']] = bBreak
            if self.Share == 0:
                if p > bBreak or ylow < bSetup and p > bEnter:
                    # Buy with all cash
                    self.buy(bar.Date[i], bar.Close[i],
                             self.Cash / bar.Close[i])

            else:
                self.Asset += self.Share * (bar.Close[i] - bar.Close[i - 1])
                if self.checklimit(bar.index[i], bar.Close[i]) == 0:
                    if yhigh > sSetup and p < sEnter:
                        # Sell all shares
                        self.liquidate(bar.Date[i], bar.Close[i])

            bar.loc[i, ['Asset']] = self.Asset
            self.pdata.loc[i, ['Asset']] = self.Asset

        if istrain and self.Asset > self.bestAsset:
            self.bestAsset = self.Asset
            self.ylen = self._ylen.val
            self.mlen = self._mlen.val

    def traininit(self, _ylen, _mlen):
        self._ylen = _ylen
        self._mlen = _mlen
        self.istrainready = 1
        self.bestAsset = -np.inf

    def train(self, bar, starttime, endtime, times):
        if self.istrainready != 1:
            print('Parameters\' range is not set.')
            return
        for i in range(times):
            self._ylen.genint()
            self._mlen.genint()
            while self._ylen.val == self._mlen.val:
                self._ylen.genint()
                self._mlen.genint()
            if self._ylen.val > self._mlen.val:
                self._ylen.val, self._mlen.val = self._mlen.val, self._ylen.val
            self.test(bar, starttime, endtime, 1)


class _bld(Strategy):
    k = 0  # best parameter
    t = 0
    bestAsset = 0
    _k = Parameter()  # train parameter
    _t = Parameter()
    istrainready = 0

    def __init__(self):
        pass

    def setlen(self, k=1, t=10):
        print(self)
        self.k = k
        self.t = t

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=1):
        self.cal(bar, BMbar, starttime, endtime)
        self.data = yf.Ticker(token)
        print('-------------------RESULT----------------------')
        print("Stock:", token)
        print("startCash:", self.startCash)
        print("Asset:", round(self.Asset, 2))
        print("Cash:", round(self.Cash, 2))
        print("Share:", round(self.Share, 2))
        print("Alpha:", round(self.Alpha, 2))
        print("Sharpe:", round(self.Sharpe, 2))
        print("buy:", self.buypoint)
        print("sell:", self.sellpoint)
        print("Return: {:.2%}".format(self.Return))
        print('-----------------------------------------------')
        bar = bar[pd.to_datetime(starttime) <= bar['Date']]
        bar = bar[bar['Date'] <= pd.to_datetime(endtime)]
        self.pdata = self.pdata[pd.to_datetime(starttime) <= self.pdata['Date']]
        self.pdata = self.pdata[self.pdata['Date'] <= pd.to_datetime(endtime)]
        plt.clf()
        plt.subplot(2, 1, 1)
        plt.plot(bar['Date'], bar['Close'])
        plt.plot(self.pdata['Date'], self.pdata['UP'])
        plt.plot(self.pdata['Date'], self.pdata['DOWN'])
        label = ["Close", "UP", "DOWN"]
        plt.legend(label)
        plt.ylabel("Price(USD)")
        plt.subplot(2, 1, 2)
        plt.ylabel("Asset(USD)")
        plt.plot(bar['Date'], self.pdata['Asset'])
        plt.tight_layout()
        if saveimg:
            plt.savefig('./Result/' + token + dt.datetime.now().strftime('%H%M%S'))

    def test(self, bar, starttime, endtime, istrain=0):
        self.clear()
        if istrain:
            k = self._k.val
            t = self._t.val
        else:
            k = self.k
            t = self.t
        for i in range(k + 1, len(bar)):
            if not (pd.to_datetime(starttime) <= bar.Date[i] <= pd.to_datetime(endtime)):
                continue
            self.pdata.loc[i, ['Date']] = bar.loc[i, ['Date']]
            # cal MA
            ma = bar.Close[i - t:i].mean()
            up = (ma + k * bar.Close.std()) / 1.3
            down = (ma - k * bar.Close.std()) * 1.3
            p = bar.Close[i - 1]
            self.pdata.loc[i, ['UP']] = up  # record , get ready for plot
            self.pdata.loc[i, ['DOWN']] = down
            if self.Share == 0:
                if p < down:
                    # Buy with all cash
                    self.buy(bar.Date[i], bar.Close[i], self.Cash / bar.Close[i])
            else:
                self.Asset += self.Share * (bar.Close[i] - bar.Close[i - 1])  # Hold
                if self.checklimit(bar.index[i], bar.Close[i]) == 0:
                    if p > up:
                        # Sell all shares
                        self.liquidate(bar.Date[i], bar.Close[i])
            bar.loc[i, ['Asset']] = self.Asset
            self.pdata.loc[i, ['Asset']] = self.Asset
        if istrain and self.Asset > self.bestAsset:
            self.bestAsset = self.Asset
            self.k = self._k.val
            self.t = self._t.val

    def traininit(self, _k, _t):
        self._k = _k
        self._t = _t
        self.istrainready = 1
        self.bestAsset = -np.inf

    def train(self, bar, starttime, endtime, times):
        if self.istrainready != 1:
            print('Parameters\' range is not set.')
            return
        for i in range(times):
            self._k.genint()
            self._t.genint()
            self.test(bar, starttime, endtime, 1)


class _LSTM(Strategy):
    def __init__(self):
        pass

    def set_parameter(self, the_mem_days=15, pre_days=10, the_lstm_layers=1, the_dense_layers=1, the_units=32):
        self.the_mem_days = the_mem_days
        self.pre_days = pre_days
        self.the_lstm_layers = the_lstm_layers
        self.the_dense_layers = the_dense_layers
        self.the_units = the_units

    def LSTM_pretreatment(self, bar):
        bar.set_index(bar['Date'], inplace=True)
        bar = bar.loc[:, ['Open', 'High', 'Low', 'Close', 'Volume']]
        return bar

    def Stock_Price_LSTM_Data_Processing(self, bar):
        bar = self.LSTM_pretreatment(bar)
        bar.dropna(inplace=True)
        bar.sort_index(inplace=True)
        bar['label'] = bar['Close'].shift(-self.pre_days)

        scaler = StandardScaler()
        sca_X = scaler.fit_transform(bar.iloc[:, :-1])

        # mem_his_days = 10 #记忆天数

        deq = deque(maxlen=self.the_mem_days)

        X = []
        for i in sca_X:
            deq.append(list(i))
            if len(deq) == self.the_mem_days:
                X.append(list(deq))

        X = X[:-self.pre_days]

        y = bar['label'].values[self.the_mem_days - 1:-self.pre_days]

        X = np.array(X)
        y = np.array(y)

        return X, y

    def get_LSTM_model(self, bar, endtime):
        self.clear()
        print('It may take some time to fit the model, please wait.^_^')
        filepath = 'D:python/IQSRS/app01/models/' + f'men_{self.the_mem_days}_lstm_{self.the_lstm_layers}_dense_{self.the_dense_layers}_unit_{self.the_units}'
        checkpoint = ModelCheckpoint(
            filepath=filepath,
            save_weights_only=False,
            monitor='val_mape',
            mode='min',
            save_best_only=True)

        bar = bar.loc[pd.to_datetime(bar.index) < pd.to_datetime(endtime), :]

        X, y = self.Stock_Price_LSTM_Data_Processing(bar)

        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.1)

        model = Sequential()
        model.add(LSTM(self.the_units, input_shape=X.shape[1:], activation='relu', return_sequences=True))
        model.add(Dropout(0.1))

        for i in range(self.the_lstm_layers):
            model.add(LSTM(self.the_units, activation='relu', return_sequences=True))
            model.add(Dropout(0.1))

        model.add(LSTM(self.the_units, activation='relu'))
        model.add(Dropout(0.1))

        for i in range(self.the_dense_layers):
            model.add(Dense(self.the_units, activation='relu'))
            model.add(Dropout(0.1))

        model.add(Dense(1))

        model.compile(optimizer='adam',
                      loss='mse',
                      metrics=['mape'])

        model.fit(X_train, y_train, batch_size=32, epochs=50, validation_data=(X_test, y_test), callbacks=[checkpoint])

    def pred_LSTM_price(self, bar):
        filename = './/models//' + f'men_{self.the_mem_days}_lstm_{self.the_lstm_layers}_dense_{self.the_dense_layers}_unit_{self.the_units}'
        best_model = load_model(filename)
        X, y = self.Stock_Price_LSTM_Data_Processing(bar)
        y_test = y
        bar_time = bar.index[-len(y_test):]
        # best_model.evaluate(X_test, y_test)
        pre = best_model.predict(X)
        return bar_time, y_test, pre

    def LSTM_buy_judge(self, bar):
        bar_time, y_test, pre = self.pred_LSTM_price(bar)
        bar1 = pd.DataFrame(pre, index=bar_time, columns=['pre'])
        bar2 = pd.DataFrame(y_test, index=bar_time, columns=['Close'])
        bar_pre = pd.merge(bar1, bar2, left_index=True, right_index=True)
        bar_pre.set_index(bar_time)
        bar_pre['pred_profit'] = bar_pre['pre'] - bar_pre['pre'].shift(1)
        bar_pre.iloc[0, -1] = 0
        return bar_pre, bar_time

    def LSTM_backtest(self, bar, starttime, endtime):
        self.clear()
        bar_pre, bar_time = self.LSTM_buy_judge(bar)
        bar_pre = bar_pre[pd.to_datetime(starttime) <= bar_pre.index]
        bar_pre = bar_pre[bar_pre.index <= pd.to_datetime(endtime)]
        bar_time = bar_pre.index
        for i in range(len(bar_time)):
            pred_profit = bar_pre.loc[bar_time[i], 'pred_profit']
            if self.Share == 0:
                if pred_profit > 0:
                    self.buy(bar_pre.index[i], bar_pre.Close[i], self.Cash / bar_pre.Close[i])
            else:
                self.Asset += self.Share * (bar_pre.Close[i] - bar_pre.Close[i - 1])
                if self.checklimit(bar_pre.index[i], bar_pre.Close[i]) == 0:
                    if pred_profit < 0:
                        self.liquidate(bar_pre.index[i], bar_pre.Close[i])
            self.pdata.loc[i, ['Asset']] = self.Asset
            self.bestAsset = self.Asset
        self.pdata = self.pdata.set_index(bar_time)

    def show(self, token, bar, BMbar, starttime, endtime, saveimg=0):
        self.cal(bar, BMbar, starttime, endtime)
        self.data = yf.Ticker(token)
        print('-------------------RESULT----------------------')
        print("Stock:", token)
        print("startCash:", self.startCash)
        print("Asset:", round(self.Asset, 2))
        print("Cash:", round(self.Cash, 2))
        print("Share:", round(self.Share, 2))
        print("Alpha:", round(self.Alpha, 2))
        print("Sharpe:", round(self.Sharpe, 2))
        print("buy:", self.buypoint)
        print("sell:", self.sellpoint)
        print("Return: {:.2%}".format(self.Return))
        print('-----------------------------------------------')
        # plot
        bar_pre, bar_time = self.LSTM_buy_judge(bar)
        # bar = bar_pre.reset_index()
        # bar['Date'] = pd.to_datetime(bar['Date'])
        bar = bar_pre
        bar = bar[pd.to_datetime(starttime) <= bar.index]
        bar = bar[bar.index <= pd.to_datetime(endtime)]
        bar = bar.reset_index()
        self.pdata = self.pdata.reset_index()
        self.pdata = pd.merge(self.pdata, bar, how='right', left_on='Date', right_on='Date')
        self.pdata = self.pdata[pd.to_datetime(starttime) <= self.pdata['Date']]
        self.pdata = self.pdata[self.pdata['Date'] <= pd.to_datetime(endtime)]
        plt.clf()
        plt.subplot(2, 1, 1)
        plt.plot(self.pdata['Date'], self.pdata['pre'], color='red', label='prediction')
        plt.plot(self.pdata['Date'], self.pdata['Close'], color='blue', label='real price')
        plt.legend()
        plt.ylabel("Price(USD)")
        plt.subplot(2, 1, 2)
        plt.ylabel("Asset(USD)")
        plt.plot(self.pdata['Date'], self.pdata['Asset'])
        plt.tight_layout()
        # plt.show()
        if saveimg:
            plt.savefig('./Result/' + token + dt.datetime.now().strftime('%H%M%S'))


class StrLib:
    MACD = _MACD()
    RBreaker = _RBreaker()
    bld = _bld()
    LSTM = _LSTM()

    def __init__(self):
        pass

class NLP():
    def __init__(self):
        self.eng_stopwords = set(stopwords.words('english'))
        with open("D:/python/IQSRS/app01/models/NLP/forest.pkl", "rb") as f:
            self.forest = pickle.load(f)

        self.model = Word2Vec.load("D:/python/IQSRS/app01/models/NLP/300features_40minwords_10context.model")

    def clean_text(self, text, remove_stopwords=False):
        text = BeautifulSoup(text, 'html.parser').get_text()
        text = re.sub(r'[^a-zA-Z]', ' ', text)
        words = text.lower().split()
        if remove_stopwords:
            words = [w for w in words if w not in self.eng_stopwords]
        return words

    def to_review_vector(self, review):
        words = self.clean_text(review, remove_stopwords=True)
        array = np.array([self.model.wv[w] for w in words if w in self.model.wv])
        return pd.Series(array.mean(axis=0))

    def get_emo_analysis(self, word='good'):
        lm = ps.LM()
        words = lm.tokenize(word)
        score = lm.get_score(words)
        if score['Positive'] > score['Negative']:
            emo = 2
        elif score['Positive'] < score['Negative']:
            emo = 0
        else:
            try:
                text = pd.DataFrame(columns=['id', 'review'])
                text.loc[0, :] = [1, word]
                features = text.review.apply(self.to_review_vector)
                result = self.forest.predict(features)
                emo = result[0]
            except:
                emo = 1
        return emo


class Stock(StrLib, NLP):
    token = ''
    data = None
    bar = None
    Beta = np.nan


    def cal(self, bar, BMbar):
        self.Beta = self.alpha_beta(bar, BMbar, 0.03)[1]


    def __init__(self, token, timedelta, starttime, endtime, bm = 0, BMbar = 0, c=0):
        self.token = token
        self.data = yf.Ticker(token)
        self.news = self.data.news
        starttime = pd.to_datetime(starttime)
        starttime -= pd.to_timedelta('400 days')
        self.bar = self.data.history(interval=timedelta, start=starttime)
        self.bar.to_csv('./stock/' + str(self.token) + '.csv')
        self.bar = pd.read_csv('./stock/' + str(self.token) + '.csv')
        self.bar['Date'] = pd.to_datetime(self.bar['Date'])
        if bm == 0:
            if c:self.cal(self.bar, BMbar)
            self.Beta = round(self.Beta, 2)
            self.PE = round(self.data.info['forwardPE'], 2)
            self.Market_Cap = round(self.data.info["marketCap"], 2)
        self.Actions = round(self.data.actions, 2)
        self.Cash_Flow = self.data.cashflow
        self.Balance_Sheet = self.data.balance_sheet
        self.Financial_Sheet = self.data.financials




    def alpha_beta(self, stock_data, benchmark_data, rf=0):  # rf-无风险年利率
        data_len = len(stock_data)
        try:
            date_list = stock_data["Date"]
        except:
            date_list = list(stock_data.index)
        start_date = date_list[0]
        start_date = dt.datetime.strptime(str(start_date)[0:10], "%Y-%m-%d").date()
        end_date = date_list[data_len - 1]
        end_date = dt.datetime.strptime(str(end_date)[0:10], "%Y-%m-%d").date()
        date_years = (end_date - start_date).days / 365
        rf = rf ** (1 / date_years)
        seq = np.array(stock_data["Close"])
        seq_bench = np.array(benchmark_data["Close"])
        seq_return = seq[-1] / seq[0] - 1
        seq_bench_return = seq_bench[-1] / seq_bench[0] - 1
        seq_bench = seq_bench[1:] / seq_bench[0:-1] - 1
        seq = seq[1:] / seq[0:-1] - 1
        e_seq_bench = sum(seq_bench) / len(seq_bench)
        e_seq = sum(seq) / len(seq)
        cov = (seq_bench - e_seq_bench) * (seq - e_seq)
        cov = sum(cov) / len(cov)
        var = (seq_bench - e_seq_bench) ** 2
        var = sum(var) / len(var)
        beta_value = cov / var
        alpha_value = seq_return - rf - beta_value * seq_bench_return
        return (alpha_value, beta_value)

    def show(self, token, bar, BMbar):
        print('-----------------STOCK INFO--------------------')
        print("Stock:", token)
        print("Beta:", self.Beta)
        print("PE:", self.PE)
        print("Market Cap:", self.Market_Cap)
        print("Actions:", self.Actions)
        print("Cash Flow:", self.Cash_Flow)
        print("Balance Sheet:", self.Balance_Sheet)
        print("Financial Sheet:", self.Financial_Sheet)
        for i in self.news:
            print("News Title:", i['title'], ". Related Tickers:", i['relatedTickers'], ". Publish Time:",
                  i['providerPublishTime'], ". Emotional Analysis:", self.get_emo_analysis(i['title']))
        print('-----------------------------------------------')


class SelResult:
    Rank = []

    def __init__(self):
        pass


class SelStrategy(SelResult):

    def __init__(self):
        pass

    def train(self, Stocks, starttime, endtime):
        pass

    def test(self, Stocks, starttime, endtime):
        pass

    def show(self, Stocks, starttime, endtime):
        pass


class _MF(SelStrategy):
    def __init__(self):
        pass


class _SR(SelStrategy):
    def __init__(self):
        pass


class SelStrLib(SelStrategy):
    SR = _SR()
    MF = _MF()


class StockLib:
    Stocks = []
    BM = None
    SelStrLib = SelStrLib()
    isBMready = 0

    def __init__(self):
        pass

    def addstock(self, Stock):
        if self.isBMready == 0:
            print('BenchMark has not set yet.')
            sys.exit(0)
        self.Stocks.append(Stock)

    def setBM(self, Stock):
        self.BM = Stock
        self.isBMready = 1