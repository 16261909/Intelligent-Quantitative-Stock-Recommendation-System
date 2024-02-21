"""IQSRS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
import sys
# sys.path.append('..')

from app01.views import show, manage, login

urlpatterns = [
    path('login/', login.login),
    path('logout/', login.logout),

    path('manage/user/', manage.manageuser),
    path('manage/stock/', manage.managestock),
    path('manage/stock/add/', manage.stockadd),
    path('manage/backtest/', manage.managebacktest),
    path('manage/user/mod/', manage.usermod),
    path('manage/user/add/', manage.useradd),

    path('stock/', show.showstock),
    path('stock/bar/', show.showbar),
    path('stock/pip/', show.showpip),
    path('overview/', show.overview),
    path('home/', show.home),
    path('result/', show.result),
    path('resultlist/', show.resultlist),
    path('backtest/', show.backtest),
]


