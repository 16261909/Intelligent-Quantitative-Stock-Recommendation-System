from django.db import models
# python manage.py makemigrations
# python manage.py migrate
# Create your models here.

# insert into app01_userinfo(username, password, phone, investage, asset, createtime, risktolerance) values('steven','123','123',0,0,'2022-07-24',0);
class UserInfo(models.Model):
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=16)
    phone = models.CharField(max_length=11)
    investage = models.SmallIntegerField()
    asset = models.DecimalField(max_digits=12, decimal_places=2)
    createtime = models.DateField(auto_now_add=True)
    risktolerance = models.SmallIntegerField()

# insert into app01_stockinfo(ticker, bm) values('SPY',1),('MSFT',0),('AAPL',0),('TSLA',0),('NVDA',0),('INTC',0),('AMD',0),('AMZN',0),('ZM',0),('NFLX',0),('BABA',0),('GOOG',0),('SONY',0),('PYPL',0),('UBER',0),('META',0),('TWTR',0),('SNAP',0),('PINS',0),('AMC',0);
class StockInfo(models.Model):
    ticker = models.CharField(max_length=4, unique=True)
    pe = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    marketcap = models.BigIntegerField(null=True, blank=True)
    beta = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bm_choices = (
        (0, 'No'),
        (1, 'Yes')
    )
    bm = models.SmallIntegerField(verbose_name='benchmark', choices=bm_choices, default=0)
    def __str__(self):
        return self.ticker

class PriceInfo(models.Model):
    sid = models.ForeignKey(verbose_name='stockid', to="StockInfo", to_field="id", on_delete=models.CASCADE)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    open = models.DecimalField(max_digits=12, decimal_places=2)
    close = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=6, decimal_places=2)
    volume = models.IntegerField()
    ctime = models.DateField(verbose_name='closetime')
    interval_choices = (
        (0, '1d'),
        (1, '5d'),
        (2, '1mo'),
        (3, '1y')
    )
    interval = models.SmallIntegerField(choices=interval_choices, default=0)

class MACDBestPara(models.Model):
    sma = models.SmallIntegerField(default=20)
    lma = models.SmallIntegerField(default=60)
    sid = models.ForeignKey(verbose_name='stockid', to="StockInfo", to_field="id", on_delete=models.CASCADE)

# insert into app01_strlist(name) value('MACD'),('BOLL'),('RBreaker'),('LSTM');
class StrList(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class StrInfo(models.Model):
    strid = models.ForeignKey(verbose_name='strategyid', to="StrList", to_field="id", on_delete=models.CASCADE)
    starttime = models.DateField()
    endtime = models.DateField()
    stopgainratio = models.DecimalField(max_digits=5, decimal_places=2)
    stoplossratio = models.DecimalField(max_digits=5, decimal_places=2)
    startcash = models.DecimalField(max_digits=12, decimal_places=2)
    parai1 = models.SmallIntegerField(null=True, blank=True)
    parai2 = models.SmallIntegerField(null=True, blank=True)
    parai3 = models.SmallIntegerField(null=True, blank=True)
    parai4 = models.SmallIntegerField(null=True, blank=True)
    parai5 = models.SmallIntegerField(null=True, blank=True)
    paraf1 = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    paraf2 = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)

class BTInfo(models.Model): # backtest
    sid = models.ForeignKey(verbose_name='stockid', to="StockInfo", to_field="id", on_delete=models.CASCADE)
    uid = models.ForeignKey(verbose_name='userid', to="UserInfo", to_field="id", on_delete=models.CASCADE)
    paraid = models.ForeignKey(verbose_name='parameterid', to="StrInfo", to_field="id", on_delete=models.CASCADE)
    asset = models.DecimalField(max_digits=12, decimal_places=2)
    cash = models.DecimalField(max_digits=12, decimal_places=2)
    share = models.DecimalField(max_digits=12, decimal_places=2)
    ret = models.DecimalField(verbose_name='return',max_digits=12, decimal_places=2)
    sharpe = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    alpha = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class BSInfo(models.Model): # BuySell
    btid = models.ForeignKey(verbose_name='backtestid', to='BTInfo', to_field='id', on_delete=models.CASCADE)
    type_choices = (
        (0, 'buy'),
        (1, 'sell')
    )
    type = models.SmallIntegerField(choices=type_choices, default=0)
    time = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

class NewsInfo(models.Model):
    sid = models.ForeignKey(verbose_name='stockid', to='StockInfo', to_field='id', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    emo_choices = (
        (0, 'negative'),
        (1, 'neutral'),
        (2, 'positive')
    )
    emo = models.SmallIntegerField(verbose_name='emotion', choices=emo_choices, default=1)

#
# class tmp(models.Model):
#     # add column
#     data = models.IntegerField(null=True, blank=True)
#     data1 = models.IntegerField(default=2)
#     fk1 = models.ForeignKey(to="UserInfo", to_field="id", on_delete=models.CASCADE)  # fk1_id
#     fk1 = models.ForeignKey(to="UserInfo", to_field="id", null=True, blank=True, on_delete=models.SET_NULL)  # fk1_id
#

# tmp.objects.create(data=11)

# tmp.objects.filter(id=3).delete()
# tmp.objects.all().delete()

# datalist = UserInfo.objects.all()
# datalist = UserInfo.objects.filter(id=1) #dataset
# datalist = UserInfo.objects.filter(id=1).first() #object
# for obj in datalist:
#     obj.id
#     obj.username

# tmp.objects.all().update(password=999)