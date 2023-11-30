from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView, UpdateView
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage
from draganddrop.views.home.home_common import CommonView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import ApprovalWorkflowEditForm, FirstApproverSetForm, SecondApproverSetForm
from accounts.models import User,Service,Company
from contracts.models import Plan, Contract, FileupDetail
# import datetime
from django.db.models import Q
from django.conf import settings
import math
import random
import string
import threading
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.core import serializers

# # 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired
from django.contrib.sites.shortcuts import get_current_site

# フロントへメッセージ送信
from django.contrib import messages

# 時刻取得
from datetime import datetime, timedelta
import pytz


"""
承認ワークフロー
"""
class ApprovalWorkflowView(TemplateView,CommonView):
    template_name = 'draganddrop/ApprovalWorkflowView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        service = Service.objects.get(name="FileUP!")

        user_approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        context["user_approval_workflow_id"] = user_approval_workflow.id

        # 承認ワークフローテーブル情報取得
        user_approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id)
        context["user_approval_workflow_qs"] = user_approval_workflow

        # 第一承認者テーブル情報取得
        first_approvers = FirstApproverRelation.objects.filter(company_id=user.company.id)
        first_approver_list = []
        first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))

        # IDをstrに直してリストに追加
        for first_approver_uuid_1 in first_approver_list_raw_1:
            first_approver_uuid_string_1 = str(first_approver_uuid_1)
            first_approver_list.append(first_approver_uuid_string_1)

        first_approver_qs = User.objects.filter(id__in=first_approver_list)
        # print("---------- first_approver_qs ---------", first_approver_qs)

        context["first_approver_qs"] = first_approver_qs


        # 第二承認者テーブル情報取得
        second_approvers = SecondApproverRelation.objects.filter(company_id=user.company.id)
        second_approver_list = []
        second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))

        # IDをstrに直してリストに追加
        for second_approver_uuid_1 in second_approver_list_raw_1:
            second_approver_uuid_string_1 = str(second_approver_uuid_1)
            second_approver_list.append(second_approver_uuid_string_1)

        second_approver_qs = User.objects.filter(id__in=second_approver_list)
        # print("---------- second_approver_qs ---------", second_approver_qs)

        context["second_approver_qs"] = second_approver_qs

        # ログインユーザーが一次承認者、二次承認者に設定されているApprovalManageを取得
        user_approval_manages = ApprovalManage.objects.filter(
            Q(first_approver=user.id) | Q(second_approver=user.id)
        ).distinct()
        # print("---------- user_approval_manages ---------", user_approval_manages)

        context["user_approval_manages"] = user_approval_manages

        return context


"""
基本設定 編集画面
"""
class ApprovalWorkflowEditView(LoginRequiredMixin, CommonView, UpdateView):
    model = ApprovalWorkflow
    template_name = 'draganddrop/ApprovalWorkflowEdit.html'
    form_class = ApprovalWorkflowEditForm

    # def get_form_kwargs(self):
    #     # formにログインユーザーを渡す
    #     kwargs = super(ApprovalWorkflowEditView, self).get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     kwargs['pk'] = self.kwargs['pk']
    #     return kwargs

    def form_valid(self, form):

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        # 変更前の設定を取得
        user_approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        # print("-------------- 変更前の設定 承認ワークフロー", user_approval_workflow.is_approval_workflow)
        # print("-------------- 変更前の設定 承認形式", user_approval_workflow.approval_format)

        # フォームからDBオブジェクトを仮生成
        approval_workflow_edit = form.save(commit=False)
        # print("-------------- 変更後の設定 承認ワークフロー", approval_workflow_edit.is_approval_workflow)
        # print("-------------- 変更後の設定 承認形式", approval_workflow_edit.approval_format)

        # 承認ワークフローに変更があった場合
        if not user_approval_workflow.is_approval_workflow == approval_workflow_edit.is_approval_workflow:
            # print("-------------- 承認ワークフローに変更がありました")
            # 操作履歴を残す
            approval_operation = ApprovalOperationLog.objects.create(
                operation_user = self.request.user.id,
                operation_user_company_id = login_admin_user.company.id,
                operation_date = datetime.now(),
                operation_content = 1
            )
            approval_operation.save()

        # 承認ワークフローで1を選択している場合
        if approval_workflow_edit.is_approval_workflow == 1:
            # 承認形式に変更があった場合
            if not user_approval_workflow.approval_format == approval_workflow_edit.approval_format:
                # print("-------------- 承認形式に変更がありました")
                # 操作履歴を残す
                approval_operation = ApprovalOperationLog.objects.create(
                    operation_user = self.request.user.id,
                    operation_user_company_id = login_admin_user.company.id,
                    operation_date = datetime.now(),
                    operation_content = 2
                )
                approval_operation.save()

        # 承認ワークフローを「使用しない」を選択した場合
        if approval_workflow_edit.is_approval_workflow == 2:
            # 承認形式をNoneに設定
            approval_workflow_edit.approval_format = None

        # 保存
        approval_workflow_edit.save()

        # メッセージを返す
        messages.success(self.request, "基本情報を編集しました。")

        return redirect('draganddrop:approval_workflow')


"""
第一承認者設定画面
"""
class FirstApproverSetView(LoginRequiredMixin, CommonView, FormView):
    model = FirstApproverRelation
    template_name = 'draganddrop/FirstApproverSetView.html'
    form_class = FirstApproverSetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # service = Service.objects.get(name="FileUP!")

        # ログインユーザーの会社IDと一致する第一書委任者の情報を取得
        first_approver_users = FirstApproverRelation.objects.filter(company_id=user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        if first_approver_users:
            # リスト化
            first_approver_users_list = []
            first_approver_users_list_raw_1 = list(first_approver_users.values_list('first_approver', flat=True))

            # IDをstrに直してリストに追加
            for first_approver_user_uuid_1 in first_approver_users_list_raw_1:
                first_approver_user_uuid_string_1 = str(first_approver_user_uuid_1)
                first_approver_users_list.append(first_approver_user_uuid_string_1)

            first_approver_users_qs = User.objects.filter(id__in=first_approver_users_list)
            # print("---------- first_approver_users_qs ---------", first_approver_users_qs)# <QuerySet [<User: 比嘉 太郎 / 69523@test.jp>]>

            context["first_approver_users"] = first_approver_users_qs

            context["first_approver_count"] = first_approver_users_qs.count()

        else:
            context["first_approver_count"] = 0

        return context


    # formに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(FirstApproverSetView, self).get_form_kwargs()

        # 第一承認者に指定されているユーザーのリストをformに渡す
        first_approver_lists = []
        first_approver_users = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        if first_approver_users:
            for first_approver in first_approver_users:
                # リストにユーザーのIDを追加
                first_approver_lists.append(first_approver.first_approver)
        kwargs.update({'first_approver_lists': first_approver_lists})

        # 第二承認者に指定されているユーザーのリストをformに渡す
        second_approver_lists = []
        second_approver_users = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        # 第二承認者に指定されているユーザーを取り出す
        if second_approver_users:
            for second_approver in second_approver_users:
                # リストにユーザーのIDを追加
                second_approver_lists.append(second_approver.second_approver)
        kwargs.update({'second_approver_lists': second_approver_lists})

        # ログインしている管理者が所属する会社をformにわたす
        kwargs.update({'admin_user_company': self.request.user.company})

        return kwargs


    # 共同権限付与
    def post(self, request, *args, **kwargs):

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        # POSTで送られてきた値を取得
        user_id_list = request.POST.getlist('first_approver')

        # pkと一致するユーザーを取得
        users = User.objects.filter(pk__in=user_id_list)

        # 第一承認者を追加する
        for user in users:
            # print("--------- user", user)
            first_approver_relation = FirstApproverRelation.objects.create(
                company_id = login_admin_user.company.id,
                first_approver = user.id
            )
            first_approver_relation.save()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 3
        )
        approval_operation.save()

        message = f'第一承認者を設定しました'
        messages.success(self.request, message)

        return HttpResponseRedirect(reverse('draganddrop:first_approver_set'))


"""
第一承認者権限の削除(個別)
"""
class FirstApproverDeleteView(View):

    def post(self, request, *args, **kwargs):

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        user_id = self.kwargs['pk']

        user_obj = User.objects.filter(pk=user_id).first()
        print("----------- user_obj", user_obj)# 比嘉 太郎 / 69523@test.jp

        # 削除対処の第一承認者のレコードを取得
        del_co_admin_user = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id, first_approver=user_id).first()
        # print("----------- del_co_admin_user", del_co_admin_user)

        del_co_admin_user.delete()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 3
        )
        approval_operation.save()

        # メッセージを返す
        messages.success(self.request, "第一承認者権限を取り消しました")

        return HttpResponseRedirect(reverse('draganddrop:first_approver_set'))



"""
第二承認者設定画面
"""
class SecondApproverSetView(LoginRequiredMixin, CommonView, FormView):
    model = SecondApproverRelation
    template_name = 'draganddrop/SecondApproverSetView.html'
    form_class = SecondApproverSetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # service = Service.objects.get(name="FileUP!")

        # ログインユーザーの会社IDと一致する第一書委任者の情報を取得
        second_approver_users = SecondApproverRelation.objects.filter(company_id=user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        if second_approver_users:
            # リスト化
            second_approver_users_list = []
            second_approver_users_list_raw_1 = list(second_approver_users.values_list('second_approver', flat=True))

            # IDをstrに直してリストに追加
            for second_approver_user_uuid_1 in second_approver_users_list_raw_1:
                second_approver_user_uuid_string_1 = str(second_approver_user_uuid_1)
                second_approver_users_list.append(second_approver_user_uuid_string_1)

            second_approver_users_qs = User.objects.filter(id__in=second_approver_users_list)
            # print("---------- second_approver_users_qs ---------", second_approver_users_qs)# <QuerySet [<User: 比嘉 太郎 / 69523@test.jp>]>

            context["second_approver_users"] = second_approver_users_qs

            context["second_approver_count"] = second_approver_users_qs.count()

        else:
            context["second_approver_count"] = 0

        return context


    # formに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(SecondApproverSetView, self).get_form_kwargs()

        # 第二承認者に指定されているユーザーのリストをformに渡す
        second_approver_lists = []
        second_approver_users = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        # 第二承認者に指定されているユーザーを取り出す
        if second_approver_users:
            for second_approver in second_approver_users:
                second_approver_lists.append(second_approver.second_approver)
        kwargs.update({'second_approver_lists': second_approver_lists})

        # 第一承認者に指定されているユーザーのリストをformに渡す
        first_approver_lists = []
        first_approver_users = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        if first_approver_users:
            for first_approver in first_approver_users:
                first_approver_lists.append(first_approver.first_approver)
        kwargs.update({'first_approver_lists': first_approver_lists})

        # ログインしている管理者が所属する会社を取得
        kwargs.update({'admin_user_company': self.request.user.company})

        return kwargs


    # 共同権限付与
    def post(self, request, *args, **kwargs):

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        # POSTで送られてきた値を取得
        user_id_list = request.POST.getlist('second_approver')

        # pkと一致するユーザーを取得
        users = User.objects.filter(pk__in=user_id_list)

        # 第一承認者を追加する
        for user in users:
            # print("--------- user", user)
            second_approver_relation = SecondApproverRelation.objects.create(
                company_id = login_admin_user.company.id,
                second_approver = user.id
            )
            second_approver_relation.save()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 4
        )
        approval_operation.save()

        message = f'第二承認者を設定しました'

        messages.success(self.request, message)

        return HttpResponseRedirect(reverse('draganddrop:second_approver_set'))


"""
第二承認者権限の削除(個別)
"""
class SecondApproverDeleteView(View):

    def post(self, request, *args, **kwargs):

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        user_id = self.kwargs['pk']

        # 削除対処の第一承認者のレコードを取得
        del_co_admin_user = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id, second_approver=user_id).first()
        # print("----------- del_co_admin_user", del_co_admin_user)

        del_co_admin_user.delete()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 4
        )
        approval_operation.save()

        # メッセージを返す
        messages.success(self.request, "第二承認者権限を取り消しました")

        return HttpResponseRedirect(reverse('draganddrop:second_approver_set'))


"""
操作ログ
"""
class ApprovalLogView(TemplateView,CommonView):
    template_name = 'draganddrop/ApprovalLogView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # current_user = User.objects.filter(pk=self.request.user.id).first()
        # print("-------------- current_user", current_user)
        # print("-------------- display_name", current_user.display_name)


        # 操作履歴テーブル情報取得
        approval_operation_logs = ApprovalOperationLog.objects.filter(operation_user_company_id=self.request.user.company.id)

        context["approval_operation_logs"] = approval_operation_logs

        return context


"""
申請一覧
"""
class ApprovalDetailView(TemplateView, CommonView):
    template_name = 'draganddrop/ApprovalDetailView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        service = Service.objects.get(name="FileUP!")

        approval_manage_pk = self.kwargs['pk']
        # print("---------------- approval_manage_pk", approval_manage_pk)

        # ApprovalManage情報取得
        approval_manage_qs = ApprovalManage.objects.filter(id=approval_manage_pk)
        context["approval_manage_qs"] = approval_manage_qs

        return context



"""
承認
"""
class ApproveView(View):

    def post(self, request, *args, **kwargs):

        approval_manage_id = self.kwargs['pk']

        # ログインしているユーザーのApprovalManageのレコードを取得
        approval_manage = ApprovalManage.objects.filter(id=approval_manage_id).first()

        # ステータスを更新
        approval_manage.approval_status = 2
        approval_manage.approval_date = datetime.now()
        approval_manage.save()

        # メッセージを返す
        message = f'承認しました'

        messages.success(self.request, message)

        return HttpResponseRedirect(reverse('draganddrop:approval_workflow'))


"""
差し戻し
"""
class DeclineApplicationView(View):

    def post(self, request, *args, **kwargs):

        approval_manage_id = self.kwargs['pk']

        # ログインしているユーザーのApprovalManageのレコードを取得
        approval_manage = ApprovalManage.objects.filter(id=approval_manage_id).first()

        # ステータスを更新
        approval_manage.approval_status = 3
        approval_manage.approval_date = None
        approval_manage.save()

        # メッセージを返す
        message = f'差戻しました'

        messages.success(self.request, message)

        return HttpResponseRedirect(reverse('draganddrop:approval_workflow'))
