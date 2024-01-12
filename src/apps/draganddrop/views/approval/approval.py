from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage, ApprovalLog
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

# AjaxでJSONを返す
from django.http import JsonResponse
import json


class ApplicationStatusCheckView(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        print("----------------- TraningStatusCheckView")

        # ログインユーザーのUploadManageを取得
        user_upload_manages = UploadManage.objects.filter(created_user=self.request.user.id)
        # print("--------------- user_upload_manages", user_upload_manages)

        # 一次承認者に設定されているユーザーを取得
        first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("--------------- first_approvers", first_approvers)

        first_approver_list = []
        first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))
        # IDをstrに直してリストに追加
        for first_approver_uuid_1 in first_approver_list_raw_1:
            first_approver_uuid_string_1 = str(first_approver_uuid_1)
            first_approver_list.append(first_approver_uuid_string_1)
        # print("--------------- first_approver_list", first_approver_list)


        # 二次承認者に設定されているユーザーを取得
        second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("--------------- second_approvers", second_approvers)

        second_approver_list = []
        second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))
        # IDをstrに直してリストに追加
        for second_approver_uuid_1 in second_approver_list_raw_1:
            second_approver_uuid_string_1 = str(second_approver_uuid_1)
            second_approver_list.append(second_approver_uuid_string_1)
        # print("--------------- second_approver_list", second_approver_list)


        for user_upload_manage in user_upload_manages:
            # print("--------------- user_upload_manage", user_upload_manage)

            # approval_manage_status_list = []
            # approval_manage_count = ""
            first_approval_manage_status_list = []
            first_approval_manage_count = ""

            # UploadManageに紐づく一次承認者のApprovalManageを取得
            # approval_manages = ApprovalManage.objects.filter(upload_mange=user_upload_manage)
            first_approval_manages = ApprovalManage.objects.filter(upload_mange=user_upload_manage, first_approver__in=first_approver_list)
            # print("--------------- approval_manages", approval_manages)# 2

            # ApprovalManage数を取得
            # approval_manage_count = approval_manages.count()
            first_approval_manage_count = first_approval_manages.count()
            # print("--------------- approval_manageの数", approval_manage_count)

            # for approval_manage in approval_manages:
            for first_approval_manage in first_approval_manages:
                # ステータスをリストに追加
                # approval_manage_status_list.append(approval_manage.approval_status)
                first_approval_manage_status_list.append(first_approval_manage.approval_status)
            # print("----------------- approval_manage_status_list", approval_manage_status_list)


            second_approval_manage_status_list = []
            second_approval_manage_count = ""

            # UploadManageに紐づく一次承認者のApprovalManageを取得
            second_approval_manages = ApprovalManage.objects.filter(upload_mange=user_upload_manage, second_approver__in=second_approver_list)
            # print("--------------- approval_manages", approval_manages)# 2

            # ApprovalManage数を取得
            second_approval_manage_count = second_approval_manages.count()
            # print("--------------- approval_manageの数", approval_manage_count)

            # for approval_manage in approval_manages:
            for second_approval_manage in second_approval_manages:
                # ステータスをリストに追加
                second_approval_manage_status_list.append(second_approval_manage.approval_status)
            # print("----------------- approval_manage_status_list", approval_manage_status_list)

            # approval_manageの数とapproval_manage_listのstatusの数を比較
            if (first_approval_manage_count == first_approval_manage_status_list.count(1)):
                print("----------------- 申請中")
                user_upload_manage.application_status = 1 # 申請中
                user_upload_manage.save()

            # elif (approval_manage_count == approval_manage_status_list.count(2)): # [2,2](3, 一次承認済み)
            elif (first_approval_manage_count == first_approval_manage_status_list.count(2)):
                print("----------------- 一次承認済み")
                user_upload_manage.application_status = 3 # 一次承認済み
                user_upload_manage.save()

            else:
                # リストの要素で最大の値を求める
                max_value = max(first_approval_manage_status_list)
                print("----------------- max_value", max_value)

                if (max_value == 2): # [1,2](2, 一次承認待ち)
                    print("----------------- 一次承認待ち")
                    user_upload_manage.application_status = 2 # 一次承認待ち
                    user_upload_manage.save()

                elif(max_value == 4): # [1,4](7, 差戻し)
                    print("----------------- 差戻し")
                    user_upload_manage.application_status = 7 # 差戻し
                    user_upload_manage.save()

                else: # [1,6](6, キャンセル)
                    print("----------------- キャンセル")
                    user_upload_manage.application_status = 6 # キャンセル
                    user_upload_manage.save()


            if second_approval_manages:
                print("----------------- 二次承認者のApprovalManageあるよ")

                # approval_manageの数とapproval_manage_listのstatusの数を比較
                if (second_approval_manage_count == second_approval_manage_status_list.count(1)):# [1,1](1, 申請中)
                    print("----------------- 二次承認者 申請中")

                elif (second_approval_manage_count == second_approval_manage_status_list.count(3)):# [3,3](5, 最終承認済み)
                    print("----------------- 二次承認者 最終承認済み")
                    user_upload_manage.application_status = 5 # 最終承認済み
                    user_upload_manage.save()

                else:
                    # リストの要素で最大の値を求める
                    max_value = max(second_approval_manage_status_list)
                    print("----------------- max_value", max_value)

                    if(max_value == 3): # [1,3](4, 最終承認待ち)
                        print("----------------- 二次承認者 最終承認待ち")
                        user_upload_manage.application_status = 4 # 最終承認待ち
                        user_upload_manage.save()

                    elif(max_value == 4): # [1,4](7, 差戻し)
                        print("----------------- 二次承認者 差戻し")
                        user_upload_manage.application_status = 7 # 差戻し
                        user_upload_manage.save()

                    elif(max_value == 6): # [1,6](6, キャンセル)
                        print("----------------- 二次承認者 キャンセル")

                    else:
                        print("----------------- 二次承認者 else")

        return context


"""
承認ワークフロー
"""
class ApprovalWorkflowView(TemplateView, CommonView, ApplicationStatusCheckView):
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

        # 第一次承認者テーブル情報取得
        first_approvers = FirstApproverRelation.objects.filter(company_id=user.company.id)
        first_approver_list = []
        first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))

        # IDをstrに直してリストに追加
        for first_approver_uuid_1 in first_approver_list_raw_1:
            first_approver_uuid_string_1 = str(first_approver_uuid_1)
            first_approver_list.append(first_approver_uuid_string_1)
        first_approver_qs = User.objects.filter(id__in=first_approver_list)
        context["first_approver_qs"] = first_approver_qs


        # 第二次承認者テーブル情報取得
        second_approvers = SecondApproverRelation.objects.filter(company_id=user.company.id)
        second_approver_list = []
        second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))

        # IDをstrに直してリストに追加
        for second_approver_uuid_1 in second_approver_list_raw_1:
            second_approver_uuid_string_1 = str(second_approver_uuid_1)
            second_approver_list.append(second_approver_uuid_string_1)
        second_approver_qs = User.objects.filter(id__in=second_approver_list)
        context["second_approver_qs"] = second_approver_qs

        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()

        if approval_workflow.is_approval_workflow == 1:
            # ログインユーザーが一次承認者、二次承認者に設定されているApprovalManageを取得
            user_approval_manages = ApprovalManage.objects.filter(
                Q(first_approver=user.id) | Q(second_approver=user.id)
            ).distinct()
            # 申請一覧に表示用
            context["user_approval_manages"] = user_approval_manages

            # 承認一覧に表示用
            user_upload_manages = UploadManage.objects.filter(created_user=user.id)
            context["user_upload_manages"] = user_upload_manages

        return context


"""
基本設定 編集画面
"""
class ApprovalWorkflowEditView(LoginRequiredMixin, CommonView, UpdateView):
    model = ApprovalWorkflow
    template_name = 'draganddrop/ApprovalWorkflowEdit.html'
    form_class = ApprovalWorkflowEditForm

    def form_valid(self, form):

        print("-------------- 基本設定 編集画面")

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
            approval_workflow_edit.approval_format == None

            # UploadManageを取得
            upload_manages = UploadManage.objects.filter(company=login_admin_user.company.id)
            print("-------------- upload_manages", upload_manages)

            upload_manage_list = []
            upload_manage_list_raw_1 = list(upload_manages.values_list('id', flat=True))

            # IDをstrに直してリストに追加
            for upload_manage_uuid_1 in upload_manage_list_raw_1:
                upload_manage_uuid_string_1 = str(upload_manage_uuid_1)
                upload_manage_list.append(upload_manage_uuid_string_1)

            # UploadManageに紐づいているApprovalManageを取得
            approval_manages = ApprovalManage.objects.filter(upload_mange__in=upload_manage_list)
            # print("-------------- approval_manages", approval_manages)

            for approval_manage in approval_manages:
                # 一次承認者の場合
                if approval_manage.first_approver:
                    # print("-------------- 一次承認者の場合")
                    approval_manage.approval_status = 2 # 一次承認済み

                    if not ApprovalLog.objects.filter(approval_manage=approval_manage, approval_operation_user=approval_manage.first_approver):
                        # print("-------------- 一次承認者の承認履歴がない")

                        # 承認履歴がない場合は承認履歴を残す
                        approval_log = ApprovalLog.objects.create(
                            approval_manage = approval_manage,
                            approval_operation_user = approval_manage.first_approver,
                            approval_operation_user_company_id = approval_manage.application_user_company_id,
                            approval_operation_date = datetime.now(),
                            approval_operation_content = 2, # 一次承認
                        )
                        approval_log.save()

                # 二次承認者の場合
                else:
                    # print("-------------- 二次承認者の場合")
                    approval_manage.approval_status = 3 # 最終承認済み

                    if not ApprovalLog.objects.filter(approval_manage=approval_manage, approval_operation_user=approval_manage.second_approver):
                        # print("-------------- 二次承認者の承認履歴がない")

                        # 承認履歴を残す
                        approval_log = ApprovalLog.objects.create(
                            approval_manage = approval_manage,
                            approval_operation_user = approval_manage.second_approver,
                            approval_operation_user_company_id = approval_manage.application_user_company_id,
                            approval_operation_date = datetime.now(),
                            approval_operation_content = 3,# 最終承認
                        )
                        approval_log.save()

                # 承認日時がNoneの場合は現在の日付を代入
                if approval_manage.approval_date == None:
                    approval_manage.approval_date = datetime.now()

                # 保存
                approval_manage.save()

        # 保存
        approval_workflow_edit.save()

        # メッセージを返す
        messages.success(self.request, "基本情報を編集しました。")

        return redirect('draganddrop:approval_workflow')


"""
一次承認者設定画面
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

        # 一次承認者に指定されているユーザーのリストをformに渡す
        first_approver_lists = []
        first_approver_users = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        if first_approver_users:
            for first_approver in first_approver_users:
                # リストにユーザーのIDを追加
                first_approver_lists.append(first_approver.first_approver)
        kwargs.update({'first_approver_lists': first_approver_lists})

        # 二次承認者に指定されているユーザーのリストをformに渡す
        second_approver_lists = []
        second_approver_users = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        # 二次承認者に指定されているユーザーを取り出す
        if second_approver_users:
            for second_approver in second_approver_users:
                # リストにユーザーのIDを追加
                second_approver_lists.append(second_approver.second_approver)
        kwargs.update({'second_approver_lists': second_approver_lists})

        # ログインしている管理者が所属する会社をformにわたす
        kwargs.update({'admin_user_company': self.request.user.company})

        return kwargs


    def post(self, request, *args, **kwargs):

        print("--------- 一次承認者設定画面")

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        # POSTで送られてきた値を取得
        user_id_list = request.POST.getlist('first_approver')

        # pkと一致するユーザーを取得
        users = User.objects.filter(pk__in=user_id_list)

        # 作成されたファイルを会社単位で全部取得
        user_company_upload_manages = UploadManage.objects.filter(company=login_admin_user.company.id)
        print("--------- user_company_upload_manages", user_company_upload_manages)

        # 一次承認者を追加する
        for user in users:
            # print("--------- user", user)
            first_approver_relation = FirstApproverRelation.objects.create(
                company_id = login_admin_user.company.id,
                first_approver = user.id
            )
            first_approver_relation.save()

            if user_company_upload_manages:
                for user_company_upload_manage in user_company_upload_manages:
                    print("--------- user_company_upload_manage", user_company_upload_manage)
                    # 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
                    if not ApprovalManage.objects.filter(first_approver=user.id, upload_mange=user_company_upload_manage):
                        first_approver_approval_manage = ApprovalManage.objects.create(
                            upload_mange = user_company_upload_manage,
                            application_title = user_company_upload_manage.title,
                            application_user = user_company_upload_manage.created_user,
                            application_date = user_company_upload_manage.created_date,
                            application_user_company_id = user_company_upload_manage.company,
                            approval_status = 1,
                            first_approver = user.id
                        )
                        first_approver_approval_manage.save()


        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 3
        )
        approval_operation.save()

        message = f'一次承認者を設定しました'
        messages.success(self.request, message)

        return HttpResponseRedirect(reverse('draganddrop:first_approver_set'))


"""
一次承認者権限の削除(個別)
"""
class FirstApproverDeleteView(View):

    def post(self, request, *args, **kwargs):

        print("--------- 一次承認者権限の削除")

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        user_id = self.kwargs['pk']

        user_obj = User.objects.filter(pk=user_id).first()
        # print("----------- user_obj", user_obj)# 比嘉 太郎 / 69523@test.jp

        # 削除対処の第一次承認者のレコードを取得
        del_co_admin_user = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id, first_approver=user_id).first()
        # print("----------- del_co_admin_user", del_co_admin_user)

        del_co_admin_user.delete()

        # ApprovalManageから削除対処のユーザーが二次承認者に設定されているレコードを全て取得
        upload_manages = ApprovalManage.objects.filter(first_approver=user_id)
        # print("--------- upload_manages", upload_manages)

        # 削除
        if upload_manages:
            upload_manages.delete()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 3
        )
        approval_operation.save()

        # メッセージを返す
        messages.success(self.request, "一次承認者権限を取り消しました")

        return HttpResponseRedirect(reverse('draganddrop:first_approver_set'))



"""
二次承認者設定画面
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

        # 二次承認者に指定されているユーザーのリストをformに渡す
        second_approver_lists = []
        second_approver_users = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("---------- first_approver_users ---------", first_approver_users)

        # 二次承認者に指定されているユーザーを取り出す
        if second_approver_users:
            for second_approver in second_approver_users:
                second_approver_lists.append(second_approver.second_approver)
        kwargs.update({'second_approver_lists': second_approver_lists})

        # 一次承認者に指定されているユーザーのリストをformに渡す
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


    def post(self, request, *args, **kwargs):

        print("--------- 二次承認者設定画面")

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        # POSTで送られてきた値を取得
        user_id_list = request.POST.getlist('second_approver')

        # pkと一致するユーザーを取得
        users = User.objects.filter(pk__in=user_id_list)

        # 作成されたファイルを会社単位で全部取得
        user_company_upload_manages = UploadManage.objects.filter(company=login_admin_user.company.id)
        # print("--------- user_company_upload_manages", user_company_upload_manages)

        # 二次承認者を追加する
        for user in users:
            # print("--------- user", user)
            second_approver_relation = SecondApproverRelation.objects.create(
                company_id = login_admin_user.company.id,
                second_approver = user.id
            )
            second_approver_relation.save()

            if user_company_upload_manages:
                for user_company_upload_manage in user_company_upload_manages:
                    # print("--------- user_company_upload_manage", user_company_upload_manage)
                    # 新しく二次承認者に設定されたユーザー分のupload_manageを作成する
                    if not ApprovalManage.objects.filter(second_approver=user.id, upload_mange=user_company_upload_manage):
                        second_approver_approval_manage = ApprovalManage.objects.create(
                            upload_mange = user_company_upload_manage,
                            application_title = user_company_upload_manage.title,
                            application_user = user_company_upload_manage.created_user,
                            application_date = user_company_upload_manage.created_date,
                            application_user_company_id = user_company_upload_manage.company,
                            approval_status = 1,
                            second_approver = user.id
                        )
                        second_approver_approval_manage.save()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 4
        )
        approval_operation.save()

        message = f'二次承認者を設定しました'

        messages.success(self.request, message)

        return HttpResponseRedirect(reverse('draganddrop:second_approver_set'))


"""
二次承認者権限の削除(個別)
"""
class SecondApproverDeleteView(View):

    def post(self, request, *args, **kwargs):

        print("--------- 二次承認者権限の削除")

        user_id = self.kwargs['pk']

        # ログインしている管理者を取得
        login_admin_user = User.objects.filter(pk=self.request.user.id).first()

        # 削除対処の二次承認者のレコードを取得
        del_co_admin_user = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id, second_approver=user_id).first()
        # print("----------- del_co_admin_user", del_co_admin_user)

        del_co_admin_user.delete()

        # ApprovalManageから削除対処のユーザーが二次承認者に設定されているレコードを全て取得
        upload_manages = ApprovalManage.objects.filter(second_approver=user_id)
        # print("--------- upload_manages", upload_manages)

        # 削除
        if upload_manages:
            upload_manages.delete()

        # 操作履歴を残す
        approval_operation = ApprovalOperationLog.objects.create(
            operation_user = self.request.user.id,
            operation_user_company_id = login_admin_user.company.id,
            operation_date = datetime.now(),
            operation_content = 4
        )
        approval_operation.save()

        # メッセージを返す
        messages.success(self.request, "二次承認者権限を取り消しました")

        return HttpResponseRedirect(reverse('draganddrop:second_approver_set'))


"""
操作ログ
"""
class ApprovalLogView(TemplateView,CommonView):
    template_name = 'draganddrop/ApprovalLogView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
        print("---------- 承認View")

        try:
            approval_manage_id = request.POST.get('approval_manage_id')

            approve_comment = request.POST.get('approve_comment')
            # print("----------------- approve_comment", approve_comment)

            # ログインしているユーザーのApprovalManageのレコードを取得
            approval_manage = ApprovalManage.objects.filter(id=approval_manage_id).first()

            first_approver = approval_manage.first_approver
            second_approver = approval_manage.second_approver

            # ログインユーザーが一次承認者の場合
            if first_approver:
                # ステータスを更新
                approval_manage.approval_status = 2
                approval_manage.approval_date = datetime.now()
                approval_manage.save()

                # 承認履歴を残す
                approval_log = ApprovalLog.objects.create(
                    approval_manage =  approval_manage,
                    approval_operation_user = self.request.user.id,
                    approval_operation_user_company_id = self.request.user.company.id,
                    approval_operation_date = datetime.now(),
                    approval_operation_content = 2,# 一次承認
                    message = approve_comment
                )
                approval_log.save()
            else:
                # ステータスを更新
                approval_manage.approval_status = 3
                approval_manage.approval_date = datetime.now()
                approval_manage.save()

                # 承認履歴を残す
                approval_log = ApprovalLog.objects.create(
                    approval_manage = approval_manage,
                    approval_operation_user = self.request.user.id,
                    approval_operation_user_company_id = self.request.user.company.id,
                    approval_operation_date = datetime.now(),
                    approval_operation_content = 3,# 最終承認
                    message = approve_comment
                )
                approval_log.save()



            # メッセージを返す
            message = f'承認しました'
            messages.success(self.request, message)

            # メッセージを生成してJSONで返す
            return JsonResponse({"status": "ok",
                                "message": "承認しました",
                                })

        except Exception as e:
            print("ERROR", e) # 'e'の中にエラーの該当行が入る
            data = {}
            data['status'] = 'ng'
            data['message'] = '承認に失敗しました'
            return JsonResponse(data)


"""
差し戻し
"""
class DeclineApplicationView(View):

    def post(self, request, *args, **kwargs):
        print("----------------- 差し戻しView")

        try:
            # approval_manage_id = self.kwargs['pk']
            approval_manage_id = request.POST.get('approval_manage_id')
            # print("----------------- approval_manage_id", approval_manage_id)

            returned_comment = request.POST.get('returned_comment')
            # print("----------------- returned_comment", returned_comment)

            # ログインしているユーザーのApprovalManageのレコードを取得
            approval_manage = ApprovalManage.objects.filter(id=approval_manage_id).first()

            # ステータス
            approval_manage.approval_status = 4

            # 差戻し日時
            approval_manage.returned_date = datetime.now()

            approval_manage.save()

            # 承認履歴を残す
            approval_log = ApprovalLog.objects.create(
                approval_manage = approval_manage,
                approval_operation_user = self.request.user.id,
                approval_operation_user_company_id = self.request.user.company.id,
                approval_operation_date = datetime.now(),
                approval_operation_content = 4,
                message = returned_comment,
            )
            approval_log.save()

            # メッセージを返す
            message = f'差戻しました'
            messages.success(self.request, message)

            # メッセージを生成してJSONで返す
            return JsonResponse({"status": "ok",
                                "message": "差戻しました",
                                })

        except Exception as e:
            print("ERROR", e) # 'e'の中にエラーの該当行が入る
            data = {}
            data['status'] = 'ng'
            data['message'] = '差戻しに失敗しました'
            return JsonResponse(data)