from django.shortcuts import render, HttpResponse, redirect
from app01.utils.form import *
from app01 import kernal


def manageuser(request):
    if request.method == 'POST':
        if request.POST.get("delid"):
            delid = request.POST.get("delid")
            UserInfo.objects.filter(id=delid).delete()
        elif request.POST.get("modid"):
            modid = request.POST.get("modid")
            row = UserInfo.objects.filter(id=modid).first()
            modform = ModUserModelForm(instance=row)
            form = AddUserModelForm()
            userdata = UserInfo.objects.all()
            return render(request, "usermanage.html",
                          {"userdata": userdata, "form": form, "modid": int(modid), "modform": modform})
    form = AddUserModelForm()
    userdata = UserInfo.objects.all()
    return render(request, "usermanage.html", {"userdata": userdata, "form": form})


def usermod(request):
    if request.method == 'GET':
        return redirect("/manage/user")
    id = request.POST.get("id")
    row = UserInfo.objects.filter(id=id).first()
    form = ModUserModelForm(data=request.POST, instance=row)
    if form.is_valid(): form.save()
    return redirect("/manage/user")


def useradd(request):
    if request.method == 'GET':
        return redirect("/manage/user")
    form = AddUserModelForm(data=request.POST)
    if form.is_valid(): form.save()
    return redirect("/manage/user")


def stockpriceupdate(bm=1, all=0):
    if all == 0:
        stock = StockInfo.objects.order_by('-id').first()
        obj = kernal.Stock(stock.ticker, '1d', '2022-01-01', '2022-07-25', bm=bm, c=0)
        # slib.addstock(obj)
        for i in range(len(obj.bar)):
            exist = PriceInfo.objects.filter(sid=stock.id).filter(ctime=obj.bar.loc[i, 'Date']).exists()
            if exist == 0:
                PriceInfo.objects.create(
                    sid=stock,
                    high=obj.bar.loc[i, 'High'],
                    low=obj.bar.loc[i, 'Low'],
                    open=obj.bar.loc[i, 'Open'],
                    close=obj.bar.loc[i, 'Close'],
                    volume=obj.bar.loc[i, 'Volume'],
                    change=(obj.bar.loc[i, 'Close'] - obj.bar.loc[i, 'Open']) / obj.bar.loc[i, 'Open'] * 100,
                    ctime=obj.bar.loc[i, 'Date']
                )
    else:
        stockdata = StockInfo.objects.all()
        for stock in stockdata:
            obj = kernal.Stock(stock.ticker, '1d', '2022-01-01', '', bm)
            # slib.addstock(obj)
            for i in range(len(obj.bar)):
                exist = PriceInfo.objects.filter(sid=stock.id).filter(ctime=obj.bar.loc[i, 'Date']).exists()
                if exist == 0:
                    PriceInfo.objects.create(
                        sid=stock,
                        high=obj.bar.loc[i, 'High'],
                        low=obj.bar.loc[i, 'Low'],
                        open=obj.bar.loc[i, 'Open'],
                        close=obj.bar.loc[i, 'Close'],
                        volume=obj.bar.loc[i, 'Volume'],
                        change=(obj.bar.loc[i, 'Close'] - obj.bar.loc[i, 'Open']) / obj.bar.loc[i, 'Open'] * 100,
                        ctime=obj.bar.loc[i, 'Date']
                    )

def stockadd(request):
    ticker = request.POST.get('ticker')
    bm = kernal.Stock('SPY', '1d', '2022-01-01', '2022-07-24', 1)
    obj = None
    BM = 0
    if request.POST.get('bm') == 'on':
        obj = kernal.Stock(ticker, '1d', '2022-01-01', '2022-07-24', 1, bm.bar, 0)
        StockInfo.objects.create(
            ticker=ticker,
            bm=1
        )
        BM = 1
    else:
        obj = kernal.Stock(ticker, '1d', '2022-01-01', '2022-07-24', 0, bm.bar, 1)
        StockInfo.objects.create(
            ticker=ticker,
            beta=obj.Beta,
            marketcap=obj.Market_Cap,
            pe=obj.PE
        )
    for item in obj.news:
        NewsInfo.objects.create(
            sid=StockInfo.objects.order_by('-id').first(),
            text=item['title'],
            emo=obj.get_emo_analysis(item['title'])
        )
    stockpriceupdate(bm=BM)
    return redirect('/manage/stock/')


def managestock(request):
    if request.method == 'POST':
        stockpriceupdate(bm=1, all=1)
    stockdata = StockInfo.objects.all()
    return render(request, 'stockmanage.html', {"stockdata": stockdata})


def managebacktest(request):
    resultlist = BTInfo.objects.all()
    return render(request, 'backtestmanage.html', {"result": resultlist})
