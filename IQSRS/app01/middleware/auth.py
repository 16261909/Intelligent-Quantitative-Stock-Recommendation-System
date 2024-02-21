from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, render, redirect


class AuthMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        sites = ['/login/', '/overview/', '/home/']
        if request.path_info in sites:
            return
        info = request.session.get('info')
        if info:
            return

        return redirect('/login/')
    # def process_response(selfs, request, response):
    #     pass