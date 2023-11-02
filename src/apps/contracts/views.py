from django.shortcuts import render

from django.views.generic import View, ListView, DetailView, TemplateView, FormView, CreateView, UpdateView, DeleteView

from accounts.models import User, Company, Service
from contracts.models import Contract, Plan

# 有効期限の保存
from datetime import datetime

# バリデーション用
from django.http import JsonResponse

# Mixin
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin


# 全てで実行させるView
class CommonView(ContextMixin):
    # ログインユーザーを返す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = User.objects.filter(pk=self.request.user.id).select_related().get()
        context["current_user"] = current_user

        url_name = self.request.resolver_match.url_name
        app_name = self.request.resolver_match.app_name

        context["url_name"] = url_name
        context["app_name"] = app_name

        return context



# """
# 試用登録
# """
# # @method_decorator(login_required, name = 'dispatch')
# class TrialContractRegAjaxView(View):
#     def post(self, request):
#         # model = Contract
#         service_id = request.POST.get('service')
#         start_date_str = request.POST.get('start_date')
#         end_date_str = request.POST.get('end_date')

#         # 保存する対象のUserオブジェクトをPKを使って取得
#         user = User.objects.get(pk = request.user.pk)

#         # 保存する対象のServiceオブジェクトをPKを使って取得
#         service = Service.objects.get(pk__iexact = service_id)

#         # サービスに関連するプランを取得
#         plan = Plan.objects.filter(service=service, is_option=False, is_trial=True).first()

#         # サービスに関連するオプションを取得
#         option = Plan.objects.filter(service=service, is_option=True, is_trial=True).first()

#         # 文字列を日付型へ変換
#         # start_date = datetime.datetime.strptime(start_date_str, '%Y/%m/%d')
#         start_date = datetime.strptime(start_date_str, '%Y/%m/%d')

#         # 変換した日付の時刻を除去
#         start_date = start_date.date()

#         # 文字列を日付型へ変換
#         # end_date = datetime.datetime.strptime(end_date_str, '%Y/%m/%d')
#         end_date = datetime.strptime(end_date_str, '%Y/%m/%d')
#         # 変換した日付の時刻を除去
#         end_date = end_date.date()


#         # TODO: 既存存在確認を追加
#         contract, created = Contract.objects.get_or_create(user=user, service=service, status="1", contract_start_date=start_date, contract_end_date=end_date)
#         contract.plan = plan
#         if option:
#             contract.option = option
#         contract.save()
#         # contract.option.set(option)

#         if created:
#             # obj.save()
#             data = {
#                 'is_created': created,
#                 'messages':'登録しました'
#             }
#         else:
#             data = {
#                 'is_created': "false",
#                 'messages':'登録に失敗しました'
#             }

#         return JsonResponse(data)
