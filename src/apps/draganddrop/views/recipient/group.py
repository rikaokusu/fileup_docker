from django.shortcuts import render
from django.views.generic import FormView, View
from draganddrop.views.home.home_common import CommonView
from ...forms import FileForm, ManageTasksStep1Form, DummyForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksUrlStep1Form, UrlDistFileUploadForm, UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
import json
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ...serializers import GetUpdateModalSerializer, GetGroupUpdateModalSerializer
#操作ログ関数
from lib.my_utils import add_log

"""
グループ一覧表示
"""
class GroupListView(FormView, CommonView):
    model = Group
    template_name = 'draganddrop/group/group_list.html'
    form_class = GroupForm
    success_url = reverse_lazy('draganddrop:group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """ group list table"""
        groups_lists = Group.objects.filter(created_user=self.request.user.id)
        context["groups_lists"] = groups_lists

        """ address list table"""
        address_lists = Address.objects.filter(is_direct_email=False)
        context["address_lists"] = address_lists

        if 'address_lists_id' in self.request.session:
            # セッションに存在するテンポラリオブジェクトモデルのIDを取得
            address_lists_id = self.request.session['address_lists_id']

            # モデルオブジェクトを取得
            address = Address.objects.filter(pk=address_lists_id)
            # アドレス帳の選択済みユーザー一覧をテンプレートへ渡す
            pk_list = address.dest_user.all().values_list('pk', flat=True)
            context["pk_list"] = list(pk_list)

        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        # グループ名を取得する。
        # 取得したグループ名を保存する。
        # group_name = form.save(commit=True)

        is_update = self.request.POST.get("is_update")
        if is_update:
            # 変更時の処理
            group_obj = Group.objects.filter(pk=int(is_update)).first()  # 変更したい対象を取得する。

            # アドレス帳から選択した値を変数に代入する。
            address_qs = form.cleaned_data['address']

            # 値を代入した変数を変更したい対象にsetする(Queryset型)
            group_obj.address.set(address_qs)

            # formに入力した値を変数に代入する。
            group_name = form.cleaned_data['group_name']
 
            group_obj.group_name = group_name

            group_obj.save()  # DBに保存する。

        else:
            # 登録時の処理
            is_update = form.save(commit=True)

        # 選択した宛先ユーザーを取得する。
        return super().form_valid(form)

#グループ登録
class GroupCreateAjaxView(View,CommonView):

    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        try:
            address_list = request.POST.getlist('address_list[]')
            address_list = [int(s) for s in address_list]
            group_name = request.POST.get('group_name')
            group_obj = Group.objects.create(group_name=group_name)
            group_obj.created_user = self.request.user.id
            #操作ログ用
            group_name = group_obj.group_name
            log_users = []
            for address in address_list:
                print('あどれすforきてる')
                log_users1 = Address.objects.get(id=address)
                log_users1 = log_users1.company_name + log_users1.last_name + log_users1.first_name + "\r\n"
                log_users.append(log_users1)
            log_users = ' '.join(log_users)
            #操作ログ終わり
            group_obj.save()

            group_obj.address.set(address_list)
            group_obj.save()
            # 操作ログ登録
            add_log(3,1,current_user,group_name,"",log_users,5,self.request.META.get('REMOTE_ADDR'))
        #     # メッセージを格納してJSONで返す
            return JsonResponse({"status": "ok",})
           
        except Exception as e:
            print("失敗",e)

            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['status'] = 'NG'
            return JsonResponse(data)

"""
グループ登録 グループ名バリデーション
"""
class GroupNameValidationView(View):
    model = Group
    template_name = 'draganddrop/address/group_list.html'

    def post(self, request):
        is_available = "true"
        if request.is_ajax():
            group_name = self.request.POST.get("group_name")
            if Group.objects.filter(created_user=self.request.user.id, group_name=group_name).exists():
                is_available = "false"
        
        return HttpResponse(is_available)

"""
グループ編集モーダルに値を返す
"""
class GetGroupUpdateModalAjaxView(APIView):

    def get(self, request, *args, **kwargs):
        # ajaxでaddress_list_idを取得
        group_list_id = kwargs['pk']

        # pkとaddress_list_idを照合。一致するObjectを取得
        group_obj = Group.objects.filter(pk=group_list_id).first()
        serializer = GetGroupUpdateModalSerializer(instance=group_obj)
        return Response(serializer.data, status.HTTP_200_OK)

class GroupUpdateAjaxView(View):

    def post(self, request, *args, **kwargs):

        try:
            group_list_id = request.POST.get('group_list_id')
            group_obj = Group.objects.filter(pk=group_list_id).first()
            group_name = request.POST.get('update_group_name')
            group_obj.group_name = group_name
            group_obj.save()
            
            address_list = request.POST.getlist('address_list[]')
            address_list = [int(s) for s in address_list]
            group_obj.address.set(address_list)
            group_obj.save()
            
            # JSONで返す
            return JsonResponse({"status": "ok",})
            print("成功")

        except Exception as e:
            print("失敗", e)
            data = {}
            data['status'] = 'NG'
            return JsonResponse(data)

"""
グループ一覧個別削除
"""

class GroupDeleteAjaxView(View, CommonView):
    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        # ダウンロードされたファイルが単体か複数か判断するための変数
        # is_type = request.POST.get('is_type')

        try:
            group_delete_id = request.POST.get('group_delete_id')
            group_delete_name = request.POST.get('group_delete_name')
            group_obj = Group.objects.filter(pk=group_delete_id).first()
            #操作ログ用
            group_address = group_obj.address.all()
            
            group_users = []
            for user in group_address:
                g_c = user.company_name
                g_l = user.last_name
                g_f = user.first_name
                user = g_c + g_l + g_f + "\r\n"
                print('ゆーざーできてる？',user)
                group_users.append(user)
            group_users = ' '.join(group_users)
            group_name = group_obj.group_name
            add_log(3,3,current_user,group_name,"",group_users,5,self.request.META.get('REMOTE_ADDR'))
            #操作ログ終わり

            group_obj.delete()

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = group_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:

            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

"""
アドレス帳一覧複数削除
"""
class GroupMultiDeleteAjaxView(View):
    def post(self, request):

        group_delete_ids = request.POST.getlist('group_delete_ids[]')

        try:
            group_lists_qs = Group.objects.filter(pk__in=group_delete_ids)

            for group_list in group_lists_qs:
                group_list.delete()

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = '削除しました'
            return JsonResponse(data)

        except Exception as e:

            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)
