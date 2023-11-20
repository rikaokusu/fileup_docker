from django.shortcuts import render
from django.views.generic import TemplateView
from draganddrop.views.home.home_common import CommonView


"""
操作ログ画面
"""
class LogView(CommonView,TemplateView):
    # model = User
    template_name = 'draganddrop/log.html'
    login_url = '/login/'