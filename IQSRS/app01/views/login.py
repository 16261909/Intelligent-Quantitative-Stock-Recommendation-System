from django.shortcuts import render, HttpResponse, redirect
from app01.utils.form import *

def login(request):
    if request.method == 'GET':
        return render(request, "login.html")
    else:
        id = request.POST.get("id")
        password = request.POST.get("password")
        exist = UserInfo.objects.filter(id=id).exists()
        if not exist:
            wrong = 'ID and password do not match.'
            return render(request, "login.html", {"wrong": wrong})
        userdata = UserInfo.objects.filter(id=id).first()
        if userdata.password != password:
            wrong = 'ID and password do not match.'
            return render(request, "login.html", {"wrong": wrong})
        else:
            request.session['info'] = {'id': id, 'username': userdata.username}
            return redirect("/overview")

def logout(request):
    request.session.clear()
    return redirect('/login/')