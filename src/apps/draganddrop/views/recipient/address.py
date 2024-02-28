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

###########################
# アドレス帳管理  #
###########################

"""
アドレス一覧表示
"""
class AddressListView(FormView, CommonView):
    model = Address
    template_name = 'draganddrop/address/address_list.html'
    form_class = AddressForm
    success_url = reverse_lazy('draganddrop:address_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """アドレス一覧"""
        address_lists = Address.objects.filter(created_user=self.request.user.id, is_direct_email=False)
        context["address_lists"] = address_lists

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        
        legal_or_individual = form.cleaned_data['legal_or_individual']
        company_name = form.cleaned_data['company_name']
        trade_name = form.cleaned_data['trade_name']
        last_name = form.cleaned_data['last_name']
        first_name = form.cleaned_data['first_name']
        
        existing_user = Address.objects.filter(email=form.cleaned_data['email'],created_user=current_user.id).first()#既存アドレスに同emailいないかCK
        if existing_user:
            address = existing_user
            address.is_direct_email = False
            
            address.legal_or_individual = legal_or_individual
            address.legal_personality = form.cleaned_data['legal_personality']
            address.legal_person_posi = form.cleaned_data['legal_person_posi']
            address.department_name = form.cleaned_data['department_name']
            address.company_name = company_name
            address.trade_name = trade_name
            address.last_name = last_name
            address.first_name = first_name
            
        else:
            address = form.save(commit=False)
            address.created_user = self.request.user.id

        if legal_or_individual == 0 or company_name:
            address.full_name_preview = company_name + " " + last_name + " " + first_name
        else:
            address.full_name_preview = trade_name + " " + last_name + " " + first_name
        address.save()
        # #操作ログ用
        email = address.email
        log_user = address.full_name_preview
        # #操作ログ終わり
        # # 操作ログ登録
        add_log(3,1,current_user,email,"",log_user,4,self.request.META.get('REMOTE_ADDR'))
        # print('アドレス帳ユーザー4')

        return super().form_valid(form)

"""
アドレス帳編集モーダルに値を返す
"""
class GetUpdateModalAjaxView(APIView):
    def get(self, request, *args, **kwargs):
        # ajaxでaddress_list_idを取得
        address_list_id = kwargs['pk']
        # pkとaddress_list_idを照合。一致するObjectを取得
        address_obj = Address.objects.filter(pk=address_list_id).first()
        serializer = GetUpdateModalSerializer(instance=address_obj)
        return Response(serializer.data, status.HTTP_200_OK)


"""
編集モーダル（変更）新規登録は一覧表示のform_valid
"""
class UpdateAddressAjaxView(APIView,CommonView):
    model = Address

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        try:
            # address_list_idを取得
            address_list_id = kwargs['pk']
            address_obj = Address.objects.filter(pk=address_list_id).first()
            data = request.data
            address_obj.legal_or_individual = data.get('legal_or_individual')
            address_obj.legal_personality = data.get('legal_personality')
            address_obj.legal_person_posi = data.get('legal_person_posi')
            address_obj.company_name = data.get('company_name')
            address_obj.trade_name = data.get('trade_name')
            address_obj.department_name = data.get('department_name')
            address_obj.last_name = data.get('last_name')
            address_obj.first_name = data.get('first_name')
            address_obj.email = data.get('email')
            address_obj.created_user = self.request.user.id
            address_obj.save()
            #操作ログ用
            email = address_obj.email
            log_user = address_obj.company_name + address_obj.last_name + address_obj.first_name
            #操作ログ終わり
            # 操作ログ登録
            add_log(3,2,current_user,email,"",log_user,4,self.request.META.get('REMOTE_ADDR'))


        # JSONで返す
            return JsonResponse({"status": "ok",})

        except Exception as e:
            data = {}
            data['status'] = 'NG'
            return JsonResponse(data)


"""
アドレス帳一覧個別削除
"""
class AddressDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        # ダウンロードされたファイルが単体か複数か判断するための変数
        # is_type = request.POST.get('is_type')

        try:
            address_delete_id = request.POST.get('address_delete_id')
            address_delete_name = request.POST.get('address_delete_name')
            address_list = Address.objects.filter(pk=address_delete_id).first()
            #操作ログ用
            email = address_list.email
            if address_list.company_name:
                log_user = address_list.company_name + address_list.last_name + address_list.first_name
            else:
                log_user = address_list.trade_name + address_list.last_name + address_list.first_name
            add_log(3,3,current_user,email,"",log_user,4,self.request.META.get('REMOTE_ADDR'))
            #操作ログ終わり
            address_list.delete()
            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = address_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:

            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

"""
アドレス帳一覧複数削除
"""
class AddressMultiDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        address_delete_ids = request.POST.getlist('address_delete_ids[]')

        try:
            address_lists = Address.objects.filter(pk__in=address_delete_ids)
            #操作ログ用
            users = []
            for user in address_lists:
                if user.company_name:
                    u_c = user.company_name
                else:
                    u_c = user.trade_name
                    
                u_l = user.last_name
                u_f = user.first_name
                user = u_c + u_l + u_f + "\r\n"
                users.append(user)
            users = ' '.join(users)

            email= []
            for user in address_lists:
                u_e = user.email + "\r\n"
                email.append(u_e)
            email = ' '.join(email)
            add_log(3,3,current_user,email,"",users,5,self.request.META.get('REMOTE_ADDR'))
            #操作ログ終わり
            for address_list in address_lists:
                address_list.delete()

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = '削除しました'
            return JsonResponse(data)

        except Exception as e:

            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

"""
アドレス帳 メールアドレスバリデーション
"""
class AddressEmailValidationView(View):
    model = Address
    template_name = 'draganddrop/address/address_list.html'

    def post(self, request):
        is_available = "true"
        if request.is_ajax():
            email = self.request.POST.get("email")
            user = self.request.user
            if Address.objects.filter(email=email,created_user=user.id,is_direct_email=False).exists():

                is_available = "false"

        return HttpResponse(is_available)

