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


    def form_valid(self, form):
        address = form.save(commit=False)
        legal_or_individual = form.cleaned_data['legal_or_individual']
        company_name = form.cleaned_data['company_name']
        last_name = form.cleaned_data['last_name']
        address.created_user = self.request.user.id
        if legal_or_individual == 0:
            first_name = form.cleaned_data['first_name']
            address.full_name_preview = company_name + " " + last_name + " " + first_name
        address.save()

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
編集モーダル(登録)
"""
class UpdateAddressAjaxView(APIView):
    model = Address

    def post(self, request, *args, **kwargs):

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

        # JSONで返す
            return JsonResponse({"status": "ok",})

        except Exception as e:
            data = {}
            data['status'] = 'NG'
            return JsonResponse(data)


"""
アドレス帳一覧個別削除
"""
class AddressDeleteAjaxView(View):
    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        # is_type = request.POST.get('is_type')

        try:
            address_delete_id = request.POST.get('address_delete_id')
            address_delete_name = request.POST.get('address_delete_name')
            address_list = Address.objects.filter(pk=address_delete_id).first()
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
class AddressMultiDeleteAjaxView(View):
    def post(self, request):

        address_delete_ids = request.POST.getlist('address_delete_ids[]')

        try:
            address_lists = Address.objects.filter(pk__in=address_delete_ids)

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
            if Address.objects.filter(email=email).exists():
                is_available = "false"
        
        return HttpResponse(is_available)

