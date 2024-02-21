import datetime
import decimal
import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.core import serializers


from app01.utils.form import *
from app01 import kernal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

def dictFetchOrm(para):
    resDic=[]
    for i in para:
        resDic.append(i)
    return json.dumps(resDic, cls=DecimalEncoder, ensure_ascii=False)

def __init__(self, token, timedelta, starttime, endtime):
    self.token = token
    # self.data = yf.Ticker(token)
    starttime = pd.to_datetime(starttime)
    starttime -= pd.to_timedelta('400 days')
    # self.bar = self.data.history(interval=timedelta, start=starttime)
    # self.bar.to_csv('./stock/' + str(self.token) + '.csv')
    self.bar = pd.read_csv('./stock/' + str(self.token) + '.csv')
    self.bar['Date'] = pd.to_datetime(self.bar['Date'])


def home(request):
    return render(request, 'home.html')

def showbar(request):
    ticker = request.GET.get('ticker')
    price = PriceInfo.objects.filter(sid__ticker=ticker).all()
    price = serializers.serialize("json", price)
    result={
        "status": True,
        "data": {
            "pricedata":price
        }
    }
    return JsonResponse(result)

def showpip(request):
    now = datetime.date.today()-datetime.timedelta(days=1)
    win = PriceInfo.objects.filter(ctime=now,change__gte=0).count()
    loss = PriceInfo.objects.filter(ctime=now,change__lt=0).count()
    result={
        "status": True,
        "data": {
            'win':win,
            'loss':loss
        }
    }
    return JsonResponse(result)

def showstock(request):
    if request.method == 'GET':
        ticker = request.GET.get('ticker')
        if not ticker or not StockInfo.objects.filter(ticker=ticker).exists():
            stockdata = StockInfo.objects.all()
            return render(request, 'stocklist.html', {"stockdata": stockdata})
        else:
            newsdata = NewsInfo.objects.filter(sid__ticker=ticker)
            stockdata = StockInfo.objects.filter(ticker=ticker).first()
            pricedata = PriceInfo.objects.filter(sid__ticker=ticker).order_by('-ctime').first()
            return render(request, 'showstock.html', {
                "ticker": ticker,
                'newsdata': newsdata,
                'stockdata': stockdata,
                'pricedata': pricedata
            })
    else:
        pass
    return render(request, 'showstock.html')


def overview(request):
    if request.method == 'POST':
        pass
    now = datetime.date.today()-datetime.timedelta(days=1)
    win = PriceInfo.objects.filter(ctime=now).order_by('-change').values('sid__ticker', 'close', 'change')[0:10]
    lose = PriceInfo.objects.filter(ctime=now).order_by('change').values('sid__ticker', 'close', 'change')[0:10]
    vol = PriceInfo.objects.filter(ctime=now).order_by('-volume').values('sid__ticker', 'close', 'change')[0:10]
    stock = StockInfo.objects.filter(bm=1).first()
    pricedata = PriceInfo.objects.filter(sid=stock.id).all()
    return render(request, 'overview.html', {
        "win": win,
        "lose": lose,
        "vol": vol,
        "ticker": stock.ticker,
        'pricedata': pricedata
    })


def backtest(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        strid = int(request.POST.get('strid'))
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        stopgain = float(request.POST.get('stopgainratio'))
        stoploss = float(request.POST.get('stoplossratio'))
        startcash = int(request.POST.get('startcash'))
        parai1 = int(request.POST.get('parai1'))
        parai2 = int(request.POST.get('parai2'))
        parai3 = request.POST.get('parai3')
        parai4 = request.POST.get('parai4')
        parai5 = request.POST.get('parai5')
        paraf1 = request.POST.get('paraf1')
        paraf2 = request.POST.get('paraf2')
        if strid == 1:
            obj = kernal.Stock(token, '1d', starttime, endtime)
            bm = kernal.Stock('SPY', '1d', starttime, endtime, bm = 1)
            obj.MACD.setcash(startcash)
            obj.MACD.set_limit(stopgain, stoploss)
            obj.MACD.setlen(parai1, parai2)
            obj.MACD.test(obj.bar, starttime, endtime)
            obj.MACD.show(token, obj.bar, bm.bar, starttime, endtime, 0)
            StrInfo.objects.create(
                strid=StrList.objects.filter(id=strid).first(),
                starttime=starttime,
                endtime=endtime,
                stopgainratio=stopgain,
                stoplossratio=stoploss,
                startcash=startcash,
                parai1=parai1,
                parai2=parai2
            )
            x = StockInfo.objects.filter(ticker=token).first()
            y = UserInfo.objects.filter(id=request.session['info']['id']).first()
            z = StrInfo.objects.order_by('-id').first()
            BTInfo.objects.create(
                sid=x,
                uid=y,
                paraid=z,
                asset=obj.MACD.Asset,
                cash=obj.MACD.Cash,
                share=obj.MACD.Share,
                ret=obj.MACD.Return,
                sharpe=obj.MACD.Sharpe,
                alpha=obj.MACD.Alpha
            )
            t = BTInfo.objects.order_by('-id').first()
            for item in obj.MACD.buypoint:
                BSInfo.objects.create(
                    btid=t,
                    type=0,
                    time=item[0],
                    price=item[1]
                )
            for item in obj.MACD.sellpoint:
                BSInfo.objects.create(
                    btid=t,
                    type=1,
                    time=item[0],
                    price=item[1]
                )
            data = BTInfo.objects.order_by('-id').first()
            ticker = str(data.sid)
            bsdata = BSInfo.objects.filter(btid=data.id).order_by('time').all()
        return render(request, 'result.html', {
            'data': data,
            'bsdata': bsdata,
            'ticker': ticker
        })
    else:
        ticker = request.GET.get('ticker')
        if not ticker:
            return redirect('/overview')
        form = BackTestModelForm()
        return render(request, 'backtest.html', {"ticker": ticker, "form": form})
    form = BackTestModelForm()
    return render(request, 'backtest.html', {"form": form})



def result(request):
    if request.method == 'POST':
        pass
    else:
        id = request.GET.get('id')
        data = BTInfo.objects.filter(id=id).first()
        ticker = str(data.sid)
        bsdata = BSInfo.objects.filter(btid=id).order_by('time').all()
    return render(request, 'result.html', {
        'data':data,
        'bsdata': bsdata,
        'ticker': ticker
    })

def resultlist(request):
    print(request.session['info']['id'])
    resultlist = BTInfo.objects.filter(uid=request.session['info']['id'])
    return render(request, 'resultlist.html', {"result": resultlist})
