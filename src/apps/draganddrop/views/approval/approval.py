from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.views.generic.base import ContextMixin
from draganddrop.views.home.home_common import resource_management_calculation_process, send_table_delete
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage,UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage, ApprovalLog, CustomGroup, UserCustomGroupRelation
from draganddrop.models import OTPUploadManage, OTPDownloadtable, GuestUploadManage, GuestUploadDownloadtable
from draganddrop.views.home.home_common import CommonView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import ApprovalWorkflowEditForm, FirstApproverSetForm, SecondApproverSetForm
from accounts.models import User,Service,Company
from contracts.models import Plan, Contract, FileupDetail
from draganddrop.forms import CustomGroupForm
import urllib.parse
import os
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
from accounts.models import Notification,User
# # 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired
from django.contrib.sites.shortcuts import get_current_site
#メール送信
from django.core.mail import send_mail

# フロントへメッセージ送信
from django.contrib import messages

# 時刻取得
from datetime import datetime, timedelta
import pytz

# AjaxでJSONを返す
from django.http import JsonResponse
import json

#操作ログ関数
from lib.my_utils import add_log
#メール送信
from django.core.mail import send_mass_mail
# テンプレート情報取得
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site

from itertools import chain

from django.urls import reverse_lazy


class ApplicationStatusCheckView(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        print("----------------- TraningStatusCheckView")

        # UploadManageを取得
        user_upload_manages = UploadManage.objects.filter(created_user=self.request.user.id)
        # print("--------------- user_upload_manages", user_upload_manages)

        # UrlUploadManageを取得
        url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id)
        # print("--------------- url_upload_manages", url_upload_manages)

        # OTPUploadManageを取得
        otp_upload_manages = OTPUploadManage.objects.filter(created_user=self.request.user.id)
        # print("--------------- otp_upload_manages", otp_upload_manages)

        # GuestUploadManageを取得
        # guest_upload_manages = GuestUploadManage.objects.filter(created_user=self.request.user.id)
        # print("--------------- guest_upload_manages", guest_upload_manages)


        # 一次承認者に設定されているユーザーを取得
        first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        first_approver_list = []
        first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))
        # IDをstrに直してリストに追加
        for first_approver_uuid_1 in first_approver_list_raw_1:
            first_approver_uuid_string_1 = str(first_approver_uuid_1)
            first_approver_list.append(first_approver_uuid_string_1)

        # 二次承認者に設定されているユーザーを取得
        second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        second_approver_list = []
        second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))
        # IDをstrに直してリストに追加
        for second_approver_uuid_1 in second_approver_list_raw_1:
            second_approver_uuid_string_1 = str(second_approver_uuid_1)
            second_approver_list.append(second_approver_uuid_string_1)



        # 通常アップロード
        if user_upload_manages:
            print("--------------- 通常アップロード")
            for user_upload_manage in user_upload_manages:

                first_approval_manage_status_list = []
                first_approval_manage_count = ""

                # UploadManageに紐づく一次承認者のApprovalManageを取得
                first_approval_manages = ApprovalManage.objects.filter(upload_manage=user_upload_manage, first_approver__in=first_approver_list)

                # ApprovalManage数を取得
                first_approval_manage_count = first_approval_manages.count()

                for first_approval_manage in first_approval_manages:
                    # ステータスをリストに追加
                    first_approval_manage_status_list.append(first_approval_manage.approval_status)

                second_approval_manage_status_list = []
                second_approval_manage_count = ""

                # UploadManageに紐づく一次承認者のApprovalManageを取得
                second_approval_manages = ApprovalManage.objects.filter(upload_manage=user_upload_manage, second_approver__in=second_approver_list)

                # ApprovalManage数を取得
                second_approval_manage_count = second_approval_manages.count()

                for second_approval_manage in second_approval_manages:
                    # ステータスをリストに追加
                    second_approval_manage_status_list.append(second_approval_manage.approval_status)

                # approval_manageの数とapproval_manage_listのstatusの数を比較
                if (first_approval_manage_count == first_approval_manage_status_list.count(1)):
                    print("----------------- 申請中")
                    user_upload_manage.application_status = 1 # 申請中
                    user_upload_manage.save()

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


        # URL共有
        if url_upload_manages:
            print("--------------- URL共有")
            for url_upload_manage in url_upload_manages:

                first_approval_manage_status_list = []
                first_approval_manage_count = ""

                # UrlUploadManageに紐づく一次承認者のApprovalManageを取得
                first_approval_manages = ApprovalManage.objects.filter(url_upload_manage=url_upload_manage, first_approver__in=first_approver_list)

                # ApprovalManage数を取得
                first_approval_manage_count = first_approval_manages.count()

                for first_approval_manage in first_approval_manages:
                    # ステータスをリストに追加
                    first_approval_manage_status_list.append(first_approval_manage.approval_status)

                second_approval_manage_status_list = []
                second_approval_manage_count = ""

                # UrlUploadManageに紐づく一次承認者のApprovalManageを取得
                second_approval_manages = ApprovalManage.objects.filter(url_upload_manage=url_upload_manage, second_approver__in=second_approver_list)

                # ApprovalManage数を取得
                second_approval_manage_count = second_approval_manages.count()

                for second_approval_manage in second_approval_manages:
                    # ステータスをリストに追加
                    second_approval_manage_status_list.append(second_approval_manage.approval_status)

                # approval_manageの数とapproval_manage_listのstatusの数を比較
                if (first_approval_manage_count == first_approval_manage_status_list.count(1)):
                    print("----------------- 申請中")
                    url_upload_manage.application_status = 1 # 申請中
                    url_upload_manage.save()

                elif (first_approval_manage_count == first_approval_manage_status_list.count(2)):
                    print("----------------- 一次承認済み")
                    url_upload_manage.application_status = 3 # 一次承認済み
                    url_upload_manage.save()

                else:
                    # リストの要素で最大の値を求める
                    max_value = max(first_approval_manage_status_list)
                    print("----------------- max_value", max_value)

                    if (max_value == 2): # [1,2](2, 一次承認待ち)
                        print("----------------- 一次承認待ち")
                        url_upload_manage.application_status = 2 # 一次承認待ち
                        url_upload_manage.save()

                    elif(max_value == 4): # [1,4](7, 差戻し)
                        print("----------------- 差戻し")
                        url_upload_manage.application_status = 7 # 差戻し
                        url_upload_manage.save()

                    else: # [1,6](6, キャンセル)
                        print("----------------- キャンセル")
                        url_upload_manage.application_status = 6 # キャンセル
                        url_upload_manage.save()


                if second_approval_manages:
                    print("----------------- 二次承認者のApprovalManageあるよ")

                    # approval_manageの数とapproval_manage_listのstatusの数を比較
                    if (second_approval_manage_count == second_approval_manage_status_list.count(1)):# [1,1](1, 申請中)
                        print("----------------- 二次承認者 申請中")

                    elif (second_approval_manage_count == second_approval_manage_status_list.count(3)):# [3,3](5, 最終承認済み)
                        print("----------------- 二次承認者 最終承認済み")
                        url_upload_manage.application_status = 5 # 最終承認済み
                        url_upload_manage.save()

                    else:
                        # リストの要素で最大の値を求める
                        max_value = max(second_approval_manage_status_list)
                        print("----------------- max_value", max_value)

                        if(max_value == 3): # [1,3](4, 最終承認待ち)
                            print("----------------- 二次承認者 最終承認待ち")
                            url_upload_manage.application_status = 4 # 最終承認待ち
                            url_upload_manage.save()

                        elif(max_value == 4): # [1,4](7, 差戻し)
                            print("----------------- 二次承認者 差戻し")
                            url_upload_manage.application_status = 7 # 差戻し
                            url_upload_manage.save()

                        elif(max_value == 6): # [1,6](6, キャンセル)
                            print("----------------- 二次承認者 キャンセル")

                        else:
                            print("----------------- 二次承認者 else")


        # OTP共有
        if otp_upload_manages:
            print("--------------- OTP共有")
            for otp_upload_manage in otp_upload_manages:

                first_approval_manage_status_list = []
                first_approval_manage_count = ""

                # UrlUploadManageに紐づく一次承認者のApprovalManageを取得
                first_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=otp_upload_manage, first_approver__in=first_approver_list)

                # ApprovalManage数を取得
                first_approval_manage_count = first_approval_manages.count()

                for first_approval_manage in first_approval_manages:
                    # ステータスをリストに追加
                    first_approval_manage_status_list.append(first_approval_manage.approval_status)

                second_approval_manage_status_list = []
                second_approval_manage_count = ""

                # UrlUploadManageに紐づく一次承認者のApprovalManageを取得
                second_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=otp_upload_manage, second_approver__in=second_approver_list)

                # ApprovalManage数を取得
                second_approval_manage_count = second_approval_manages.count()

                for second_approval_manage in second_approval_manages:
                    # ステータスをリストに追加
                    second_approval_manage_status_list.append(second_approval_manage.approval_status)

                # approval_manageの数とapproval_manage_listのstatusの数を比較
                if (first_approval_manage_count == first_approval_manage_status_list.count(1)):
                    print("----------------- 申請中")
                    otp_upload_manage.application_status = 1 # 申請中
                    otp_upload_manage.save()

                elif (first_approval_manage_count == first_approval_manage_status_list.count(2)):
                    print("----------------- 一次承認済み")
                    otp_upload_manage.application_status = 3 # 一次承認済み
                    otp_upload_manage.save()

                else:
                    # リストの要素で最大の値を求める
                    max_value = max(first_approval_manage_status_list)
                    print("----------------- max_value", max_value)

                    if (max_value == 2): # [1,2](2, 一次承認待ち)
                        print("----------------- 一次承認待ち")
                        otp_upload_manage.application_status = 2 # 一次承認待ち
                        otp_upload_manage.save()

                    elif(max_value == 4): # [1,4](7, 差戻し)
                        print("----------------- 差戻し")
                        otp_upload_manage.application_status = 7 # 差戻し
                        otp_upload_manage.save()

                    else: # [1,6](6, キャンセル)
                        print("----------------- キャンセル")
                        otp_upload_manage.application_status = 6 # キャンセル
                        otp_upload_manage.save()


                if second_approval_manages:
                    print("----------------- 二次承認者のApprovalManageあるよ")

                    # approval_manageの数とapproval_manage_listのstatusの数を比較
                    if (second_approval_manage_count == second_approval_manage_status_list.count(1)):# [1,1](1, 申請中)
                        print("----------------- 二次承認者 申請中")

                    elif (second_approval_manage_count == second_approval_manage_status_list.count(3)):# [3,3](5, 最終承認済み)
                        print("----------------- 二次承認者 最終承認済み")
                        otp_upload_manage.application_status = 5 # 最終承認済み
                        otp_upload_manage.save()

                    else:
                        # リストの要素で最大の値を求める
                        max_value = max(second_approval_manage_status_list)
                        print("----------------- max_value", max_value)

                        if(max_value == 3): # [1,3](4, 最終承認待ち)
                            print("----------------- 二次承認者 最終承認待ち")
                            otp_upload_manage.application_status = 4 # 最終承認待ち
                            otp_upload_manage.save()

                        elif(max_value == 4): # [1,4](7, 差戻し)
                            print("----------------- 二次承認者 差戻し")
                            otp_upload_manage.application_status = 7 # 差戻し
                            otp_upload_manage.save()

                        elif(max_value == 6): # [1,6](6, キャンセル)
                            print("----------------- 二次承認者 キャンセル")

                        else:
                            print("----------------- 二次承認者 else")


        # ゲストアップロード
        # if guest_upload_manages:
        #     print("--------------- ゲストアップロード")
        #     for guest_upload_manage in guest_upload_manages:

        #         first_approval_manage_status_list = []
        #         first_approval_manage_count = ""

        #         # UrlUploadManageに紐づく一次承認者のApprovalManageを取得
        #         first_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=guest_upload_manage, first_approver__in=first_approver_list)

        #         # ApprovalManage数を取得
        #         first_approval_manage_count = first_approval_manages.count()

        #         for first_approval_manage in first_approval_manages:
        #             # ステータスをリストに追加
        #             first_approval_manage_status_list.append(first_approval_manage.approval_status)

        #         second_approval_manage_status_list = []
        #         second_approval_manage_count = ""

        #         # UrlUploadManageに紐づく一次承認者のApprovalManageを取得
        #         second_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=guest_upload_manage, second_approver__in=second_approver_list)

        #         # ApprovalManage数を取得
        #         second_approval_manage_count = second_approval_manages.count()

        #         for second_approval_manage in second_approval_manages:
        #             # ステータスをリストに追加
        #             second_approval_manage_status_list.append(second_approval_manage.approval_status)

        #         # approval_manageの数とapproval_manage_listのstatusの数を比較
        #         if (first_approval_manage_count == first_approval_manage_status_list.count(1)):
        #             print("----------------- 申請中")
        #             guest_upload_manage.application_status = 1 # 申請中
        #             guest_upload_manage.save()

        #         elif (first_approval_manage_count == first_approval_manage_status_list.count(2)):
        #             print("----------------- 一次承認済み")
        #             guest_upload_manage.application_status = 3 # 一次承認済み
        #             guest_upload_manage.save()

        #         else:
        #             # リストの要素で最大の値を求める
        #             max_value = max(first_approval_manage_status_list)
        #             print("----------------- max_value", max_value)

        #             if (max_value == 2): # [1,2](2, 一次承認待ち)
        #                 print("----------------- 一次承認待ち")
        #                 guest_upload_manage.application_status = 2 # 一次承認待ち
        #                 guest_upload_manage.save()

        #             elif(max_value == 4): # [1,4](7, 差戻し)
        #                 print("----------------- 差戻し")
        #                 guest_upload_manage.application_status = 7 # 差戻し
        #                 guest_upload_manage.save()

        #             else: # [1,6](6, キャンセル)
        #                 print("----------------- キャンセル")
        #                 guest_upload_manage.application_status = 6 # キャンセル
        #                 guest_upload_manage.save()


        #         if second_approval_manages:
        #             print("----------------- 二次承認者のApprovalManageあるよ")

        #             # approval_manageの数とapproval_manage_listのstatusの数を比較
        #             if (second_approval_manage_count == second_approval_manage_status_list.count(1)):# [1,1](1, 申請中)
        #                 print("----------------- 二次承認者 申請中")

        #             elif (second_approval_manage_count == second_approval_manage_status_list.count(3)):# [3,3](5, 最終承認済み)
        #                 print("----------------- 二次承認者 最終承認済み")
        #                 guest_upload_manage.application_status = 5 # 最終承認済み
        #                 guest_upload_manage.save()

        #             else:
        #                 # リストの要素で最大の値を求める
        #                 max_value = max(second_approval_manage_status_list)
        #                 print("----------------- max_value", max_value)

        #                 if(max_value == 3): # [1,3](4, 最終承認待ち)
        #                     print("----------------- 二次承認者 最終承認待ち")
        #                     guest_upload_manage.application_status = 4 # 最終承認待ち
        #                     guest_upload_manage.save()

        #                 elif(max_value == 4): # [1,4](7, 差戻し)
        #                     print("----------------- 二次承認者 差戻し")
        #                     guest_upload_manage.application_status = 7 # 差戻し
        #                     guest_upload_manage.save()

        #                 elif(max_value == 6): # [1,6](6, キャンセル)
        #                     print("----------------- 二次承認者 キャンセル")

        #                 else:
        #                     print("----------------- 二次承認者 else")


        return context


"""
承認ワークフロー
"""
class ApprovalWorkflowView(TemplateView, CommonView, ApplicationStatusCheckView):
    template_name = 'draganddrop/ApprovalWorkflowView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        service = Service.objects.filter(name="FileUP!-Free-").first()
        if not service:
            service = Service.objects.filter(name="FileUP!-久米島町-").first()
            if not service:
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
            ).exclude(upload_manage__created_at_invalid=True).exclude(url_upload_manage__created_at_invalid=True).exclude(otp_upload_manage__created_at_invalid=True
            ).exclude(guest_upload_manage__created_at_invalid=True).distinct()

            # 申請一覧に表示用
            context["user_approval_manages"] = user_approval_manages

            # 承認一覧に表示用 ※承認設定が「無効」のときに作成したファイルは非表示
            # 通常アップロード
            upload_manages = UploadManage.objects.filter(created_user=user.id).exclude(created_at_invalid=True)
            # print("--------------- upload_manages", upload_manages)
            # URL共有
            url_upload_manages = UrlUploadManage.objects.filter(created_user=user.id).exclude(created_at_invalid=True)
            # print("--------------- url_upload_manages", url_upload_manages)
            # OTP共有
            otp_upload_manages = OTPUploadManage.objects.filter(created_user=user.id).exclude(created_at_invalid=True)
            # print("--------------- otp_upload_manages", otp_upload_manages)
            # ゲストアップロード
            # guest_upload_manages = GuestUploadManage.objects.filter(created_user=user.id).exclude(created_at_invalid=True)
            # print("--------------- guest_upload_manages", guest_upload_manages)

            # クエリーセットを合体
            report = chain(upload_manages, url_upload_manages, otp_upload_manages)
            # report = chain(upload_manages, url_upload_manages, otp_upload_manages, guest_upload_manages)
            # print("--------------- report", report)

            context["user_upload_manages"] = report

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
            upload_manages = UploadManage.objects.filter(company=login_admin_user.company.id).values_list('id', flat=True)
            # print("-------------- upload_manages", upload_manages)

            # UrlUploadManageを取得
            url_upload_manages = UrlUploadManage.objects.filter(company=login_admin_user.company.id).values_list('id', flat=True)
            # print("-------------- url_upload_manages", url_upload_manages)

            # OTPUploadManageを取得
            otp_upload_manages = OTPUploadManage.objects.filter(company=login_admin_user.company.id).values_list('id', flat=True)
            # print("-------------- otp_upload_manages", otp_upload_manages)

            # GuestUploadManageを取得
            # guest_upload_manages = GuestUploadManage.objects.filter(company=login_admin_user.company.id).values_list('id', flat=True)
            # print("-------------- guest_upload_manages", guest_upload_manages)

            # 結合
            upload_manage_list_raw_1 = upload_manages.union(url_upload_manages, url_upload_manages, otp_upload_manages)
            # upload_manage_list_raw_1 = upload_manages.union(url_upload_manages, url_upload_manages, otp_upload_manages, guest_upload_manages)
            # print("-------------- upload_manage_list_raw_1", upload_manage_list_raw_1)

            # IDをstrに直してリストに追加
            upload_manage_list = []
            for upload_manage_uuid_1 in upload_manage_list_raw_1:
                upload_manage_uuid_string_1 = str(upload_manage_uuid_1)
                upload_manage_list.append(upload_manage_uuid_string_1)


            # 紐づいているApprovalManageを取得
            approval_manages = ApprovalManage.objects.filter(manage_id__in=upload_manage_list)
            # print("-------------- approval_manages", approval_manages)

            for approval_manage in approval_manages:
                # print("-------------- approval_manage", approval_manage)

                # 一次承認者の場合
                if approval_manage.first_approver:
                    # print("-------------- 一次承認者の場合")

                    # 各承認者のApprovalManageのステータスを変更
                    approval_manage.approval_status = 2 # 一次承認済み

                    # 通常アップロード
                    if approval_manage.upload_method == 1:
                        if not ApprovalLog.objects.filter(upload_manage=approval_manage.upload_manage, approval_operation_user=approval_manage.first_approver):
                            # print("-------------- 一次承認者の承認履歴がない 通常アップロード")

                            # 承認履歴がない場合は承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                upload_manage = approval_manage.upload_manage,
                                approval_operation_user = approval_manage.first_approver,
                                approval_operation_user_position = 1,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 2, # 一次承認
                                manage_id = approval_manage.upload_manage.pk
                            )
                            approval_log.save()

                    # URL共有
                    elif approval_manage.upload_method == 2:
                        if not ApprovalLog.objects.filter(url_upload_manage=approval_manage.url_upload_manage, approval_operation_user=approval_manage.first_approver):
                            # print("-------------- 一次承認者の承認履歴がない URL共有")

                            # 承認履歴がない場合は承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                url_upload_manage = approval_manage.url_upload_manage,
                                approval_operation_user = approval_manage.first_approver,
                                approval_operation_user_position = 1,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 2, # 一次承認
                                manage_id = approval_manage.url_upload_manage.pk
                            )
                            approval_log.save()

                    # OTP共有
                    elif approval_manage.upload_method == 3:
                        if not ApprovalLog.objects.filter(otp_upload_manage=approval_manage.otp_upload_manage, approval_operation_user=approval_manage.first_approver):
                            # print("-------------- 一次承認者の承認履歴がない OTP共有")

                            # 承認履歴がない場合は承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                otp_upload_manage = approval_manage.otp_upload_manage,
                                approval_operation_user = approval_manage.first_approver,
                                approval_operation_user_position = 1,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 2, # 一次承認
                                manage_id = approval_manage.otp_upload_manage.pk
                            )
                            approval_log.save()

                    # ゲストアップロード
                    else:
                        if not ApprovalLog.objects.filter(guest_upload_manage=approval_manage.guest_upload_manage, approval_operation_user=approval_manage.first_approver):
                            # print("-------------- 一次承認者の承認履歴がない ゲストアップロード")

                            # 承認履歴がない場合は承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                guest_upload_manage = approval_manage.guest_upload_manage,
                                approval_operation_user = approval_manage.first_approver,
                                approval_operation_user_position = 1,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 2, # 一次承認
                                manage_id = approval_manage.guest_upload_manage.pk
                            )
                            approval_log.save()


                # 二次承認者の場合
                else:
                    # print("-------------- 二次承認者の場合")

                    # 各承認者のApprovalManageのステータスを変更
                    approval_manage.approval_status = 3 # 最終承認済み

                    # 通常アップロード
                    if approval_manage.upload_method == 1:
                        if not ApprovalLog.objects.filter(upload_manage=approval_manage.upload_manage, approval_operation_user=approval_manage.second_approver):
                            # print("-------------- 二次承認者の承認履歴がない 通常アップロード")

                            # 承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                upload_manage = approval_manage.upload_manage,
                                approval_operation_user = approval_manage.second_approver,
                                approval_operation_user_position = 2,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 3, # 最終承認
                                manage_id = approval_manage.upload_manage.pk
                            )
                            approval_log.save()

                    # URL共有
                    elif approval_manage.upload_method == 2:
                        if not ApprovalLog.objects.filter(url_upload_manage=approval_manage.url_upload_manage, approval_operation_user=approval_manage.second_approver):
                            # print("-------------- 二次承認者の承認履歴がない URL共有")

                            # 承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                url_upload_manage = approval_manage.url_upload_manage,
                                approval_operation_user = approval_manage.second_approver,
                                approval_operation_user_position = 2,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 3, # 最終承認
                                manage_id = approval_manage.url_upload_manage.pk
                            )
                            approval_log.save()

                    # OTP共有
                    elif approval_manage.upload_method == 3:
                        if not ApprovalLog.objects.filter(otp_upload_manage=approval_manage.otp_upload_manage, approval_operation_user=approval_manage.second_approver):
                            # print("-------------- 二次承認者の承認履歴がない OTP共有")

                            # 承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                otp_upload_manage = approval_manage.otp_upload_manage,
                                approval_operation_user = approval_manage.second_approver,
                                approval_operation_user_position = 2,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 3, # 最終承認
                                manage_id = approval_manage.otp_upload_manage.pk
                            )
                            approval_log.save()

                    # ゲストアップロード
                    else:
                        if not ApprovalLog.objects.filter(guest_upload_manage=approval_manage.guest_upload_manage, approval_operation_user=approval_manage.second_approver):
                            # print("-------------- 二次承認者の承認履歴がない ゲストアップロード")

                            # 承認履歴を残す
                            approval_log = ApprovalLog.objects.create(
                                guest_upload_manage = approval_manage.guest_upload_manage,
                                approval_operation_user = approval_manage.second_approver,
                                approval_operation_user_position = 2,
                                approval_operation_user_company_id = approval_manage.application_user_company_id,
                                approval_operation_date = datetime.now(),
                                approval_operation_content = 3, # 最終承認
                                manage_id = approval_manage.guest_upload_manage.pk
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

        # ログインユーザーの会社IDと一致する第一承認者の情報を取得
        first_approver_users = FirstApproverRelation.objects.filter(company_id=user.company.id)

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

        # ステータスが申請中のアップロードされたファイルを会社単位で取得
        # UploadManage
        user_company_upload_manages = UploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        # print("--------- user_company_upload_manages", user_company_upload_manages)

        # UrlUploadManage
        user_company_url_upload_manages = UrlUploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        # print("--------- user_company_url_upload_manages", user_company_url_upload_manages)

        # OTPUploadManage
        user_company_otp_upload_manages = OTPUploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        print("--------- user_company_otp_upload_manages", user_company_otp_upload_manages)

        # GuestUploadManage
        # user_company_guest_upload_manages = GuestUploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        # print("--------- user_company_guest_upload_manages", user_company_guest_upload_manages)


        # 一次承認者を追加する
        for user in users:
            # print("--------- user", user)
            first_approver_relation = FirstApproverRelation.objects.create(
                company_id = login_admin_user.company.id,
                first_approver = user.id
            )
            first_approver_relation.save()

            # UploadManage
            if user_company_upload_manages:
                for user_company_upload_manage in user_company_upload_manages:
                    print("--------- user_company_upload_manage", user_company_upload_manage)
                    # UploadManage 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
                    if not ApprovalManage.objects.filter(first_approver=user.id, upload_manage=user_company_upload_manage):
                        first_approver_approval_manage = ApprovalManage.objects.create(
                            upload_manage = user_company_upload_manage,
                            manage_id = user_company_upload_manage.pk,
                            application_title = user_company_upload_manage.title,
                            application_user = user_company_upload_manage.created_user,
                            application_date = user_company_upload_manage.created_date,
                            application_user_company_id = user_company_upload_manage.company,
                            approval_status = 1,
                            first_approver = user.id,
                            upload_method = 1
                        )
                        first_approver_approval_manage.save()

            # UrlUploadManage
            if user_company_url_upload_manages:
                for user_company_url_upload_manage in user_company_url_upload_manages:
                    print("--------- user_company_url_upload_manage", user_company_url_upload_manage)
                    # UrlUploadManage 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
                    if not ApprovalManage.objects.filter(first_approver=user.id, url_upload_manage=user_company_url_upload_manage):
                        first_approver_approval_manage = ApprovalManage.objects.create(
                            url_upload_manage = user_company_url_upload_manage,
                            manage_id = user_company_url_upload_manage.pk,
                            application_title = user_company_url_upload_manage.title,
                            application_user = user_company_url_upload_manage.created_user,
                            application_date = user_company_url_upload_manage.created_date,
                            application_user_company_id = user_company_url_upload_manage.company,
                            approval_status = 1,
                            first_approver = user.id,
                            upload_method = 2
                        )
                        first_approver_approval_manage.save()

            # OTPUploadManage
            if user_company_otp_upload_manages:
                for user_company_otp_upload_manage in user_company_otp_upload_manages:
                    print("--------- user_company_otp_upload_manage", user_company_otp_upload_manage)
                    # OTPUploadManage 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
                    if not ApprovalManage.objects.filter(first_approver=user.id, otp_upload_manage=user_company_otp_upload_manage):
                        first_approver_approval_manage = ApprovalManage.objects.create(
                            otp_upload_manage = user_company_otp_upload_manage,
                            manage_id = user_company_otp_upload_manage.pk,
                            application_title = user_company_otp_upload_manage.title,
                            application_user = user_company_otp_upload_manage.created_user,
                            application_date = user_company_otp_upload_manage.created_date,
                            application_user_company_id = user_company_otp_upload_manage.company,
                            approval_status = 1,
                            first_approver = user.id,
                            upload_method = 3
                        )
                        first_approver_approval_manage.save()

            # GuestUploadManage
            # if user_company_guest_upload_manages:
            #     for user_company_guest_upload_manage in user_company_guest_upload_manages:
            #         print("--------- user_company_guest_upload_manage", user_company_guest_upload_manage)
            #         # GuestUploadManage 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
            #         if not ApprovalManage.objects.filter(first_approver=user.id, guest_upload_manage=user_company_guest_upload_manage):
            #             first_approver_approval_manage = ApprovalManage.objects.create(
            #                 guest_upload_manage = user_company_guest_upload_manage,
            #                 manage_id = user_company_guest_upload_manage.pk,
            #                 application_title = user_company_guest_upload_manage.title,
            #                 application_user = user_company_guest_upload_manage.created_user,
            #                 application_date = user_company_guest_upload_manage.created_date,
            #                 application_user_company_id = user_company_guest_upload_manage.company,
            #                 approval_status = 1,
            #                 first_approver = user.id,
            #                 upload_method = 4
            #             )
            #             first_approver_approval_manage.save()


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

        # ApprovalManageから削除対処のユーザーが一次承認者に設定されているレコードを全て取得
        approval_manages = ApprovalManage.objects.filter(first_approver=user_id)

        if approval_manages:
            for approval_manage in approval_manages:
                # approval_manageのステータスが未承認の場合は削除
                if approval_manage.approval_status == 1:
                    approval_manage.delete()
                # それ以外はapproval_manageを残す
                else:
                    approval_manage.is_rogical_deleted = True
                    approval_manage.save()

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

        # ステータスが「申請中」のファイルを会社単位で全部取得
        # UploadManage
        user_company_upload_manages = UploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        # print("--------- user_company_upload_manages", user_company_upload_manages)

        # UrlUploadManage
        user_company_url_upload_manages = UrlUploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        # print("--------- user_company_url_upload_manages", user_company_url_upload_manages)

        # OTPUploadManage
        user_company_otp_upload_manages = OTPUploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        print("--------- user_company_otp_upload_manages", user_company_otp_upload_manages)

        # GuestUploadManage
        # user_company_guest_upload_manages = GuestUploadManage.objects.filter(company=login_admin_user.company.id, application_status=1)
        # print("--------- user_company_guest_upload_manages", user_company_guest_upload_manages)


        # 二次承認者を追加する
        for user in users:
            # print("--------- user", user)
            second_approver_relation = SecondApproverRelation.objects.create(
                company_id = login_admin_user.company.id,
                second_approver = user.id
            )
            second_approver_relation.save()

            # 新しく二次承認者に設定されたユーザー分のupload_manageを作成する
            if user_company_upload_manages:
                for user_company_upload_manage in user_company_upload_manages:
                    # UploadManage用
                    if not ApprovalManage.objects.filter(second_approver=user.id, upload_manage=user_company_upload_manage):
                        second_approver_approval_manage = ApprovalManage.objects.create(
                            upload_manage = user_company_upload_manage,
                            manage_id = user_company_upload_manage.pk,
                            application_title = user_company_upload_manage.title,
                            application_user = user_company_upload_manage.created_user,
                            application_date = user_company_upload_manage.created_date,
                            application_user_company_id = user_company_upload_manage.company,
                            approval_status = 1,
                            second_approver = user.id,
                            upload_method = 1
                        )
                        second_approver_approval_manage.save()


            if user_company_url_upload_manages:
                for user_company_url_upload_manage in user_company_url_upload_manages:
                    # UrlUploadManage用
                    if not ApprovalManage.objects.filter(second_approver=user.id, url_upload_manage=user_company_url_upload_manage):
                        second_approver_approval_manage = ApprovalManage.objects.create(
                            url_upload_manage = user_company_url_upload_manage,
                            manage_id = user_company_url_upload_manage.pk,
                            application_title = user_company_url_upload_manage.title,
                            application_user = user_company_url_upload_manage.created_user,
                            application_date = user_company_url_upload_manage.created_date,
                            application_user_company_id = user_company_url_upload_manage.company,
                            approval_status = 1,
                            second_approver = user.id,
                            upload_method = 2
                        )
                        second_approver_approval_manage.save()

            # OTPUploadManage
            if user_company_otp_upload_manages:
                for user_company_otp_upload_manage in user_company_otp_upload_manages:
                    print("--------- user_company_otp_upload_manage", user_company_otp_upload_manage)
                    # OTPUploadManage 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
                    if not ApprovalManage.objects.filter(second_approver=user.id, otp_upload_manage=user_company_otp_upload_manage):
                        second_approver_approval_manage = ApprovalManage.objects.create(
                            otp_upload_manage = user_company_otp_upload_manage,
                            manage_id = user_company_otp_upload_manage.pk,
                            application_title = user_company_otp_upload_manage.title,
                            application_user = user_company_otp_upload_manage.created_user,
                            application_date = user_company_otp_upload_manage.created_date,
                            application_user_company_id = user_company_otp_upload_manage.company,
                            approval_status = 1,
                            second_approver = user.id,
                            upload_method = 3
                        )
                        second_approver_approval_manage.save()

            # GuestUploadManage
            # if user_company_guest_upload_manages:
            #     for user_company_guest_upload_manage in user_company_guest_upload_manages:
            #         print("--------- user_company_guest_upload_manage", user_company_guest_upload_manage)
            #         # GuestUploadManage 新しく一次承認者に設定されたユーザー分のupload_manageを作成する
            #         if not ApprovalManage.objects.filter(second_approver=user.id, guest_upload_manage=user_company_guest_upload_manage):
            #             second_approver_approval_manage = ApprovalManage.objects.create(
            #                 guest_upload_manage = user_company_guest_upload_manage,
            #                 manage_id = user_company_guest_upload_manage.pk,
            #                 application_title = user_company_guest_upload_manage.title,
            #                 application_user = user_company_guest_upload_manage.created_user,
            #                 application_date = user_company_guest_upload_manage.created_date,
            #                 application_user_company_id = user_company_guest_upload_manage.company,
            #                 approval_status = 1,
            #                 second_approver = user.id,
            #                 upload_method = 4
            #             )
            #             second_approver_approval_manage.save()




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
        approval_manages = ApprovalManage.objects.filter(second_approver=user_id)

        if approval_manages:
            for approval_manage in approval_manages:
                # approval_manageのステータスが未承認の場合は削除
                if approval_manage.approval_status == 1:
                    approval_manage.delete()
                # それ以外はapproval_manageを残す
                else:
                    approval_manage.is_rogical_deleted = True
                    approval_manage.save()

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
        service = Service.objects.filter(name="FileUP!-Free-").first()
        if not service:
            service = Service.objects.filter(name="FileUP!-久米島町-").first()
            if not service:
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

            approval_upload_method = request.POST.get('approval_upload_method')

            # ログインしているユーザーの該当するアップロード承認のApprovalManageのレコードを取得
            approval_manage = ApprovalManage.objects.filter(id=approval_manage_id).first()

            first_approver = approval_manage.first_approver

            ###########################################################通知用定義
            # 一次承認者に設定されているユーザーを取得
            first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)#会社で指名されている固定の第一承認者
            first_approver_list = []
            first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))#first_approversから第一承認者のユーザーIDだけのリストになっている
            # IDをstrに直してリストに追加
            for first_approver_uuid_1 in first_approver_list_raw_1:
                first_approver_uuid_string_1 = str(first_approver_uuid_1)
                first_approver_list.append(first_approver_uuid_string_1)

            # 二次承認者に設定されているユーザーを取得
            second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
            second_approver_list = []
            second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))
            # IDをstrに直してリストに追加
            for second_approver_uuid_1 in second_approver_list_raw_1:
                second_approver_uuid_string_1 = str(second_approver_uuid_1)
                second_approver_list.append(second_approver_uuid_string_1)
            
            if approval_upload_method == "1":#通常アップロード
                # UploadManageに紐づく一次承認者のApprovalManageを取得
                first_approval_manages = ApprovalManage.objects.filter(upload_manage=approval_manage.upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(upload_manage=approval_manage.upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.upload_manage
                file_title = approval_manage.upload_manage.title
                file_message = approval_manage.upload_manage.message
                download_type = 'normal'
            elif approval_upload_method == "2": # URL共有
                first_approval_manages = ApprovalManage.objects.filter(url_upload_manage=approval_manage.url_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(url_upload_manage=approval_manage.url_upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.url_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.url_upload_manage
                file_title = approval_manage.url_upload_manage.title
                file_message = approval_manage.url_upload_manage.message
                download_type = 'url'
            elif approval_upload_method == "3": # OTP共有
                first_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=approval_manage.otp_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=approval_manage.otp_upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.otp_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.otp_upload_manage
                file_title = approval_manage.otp_upload_manage.title
                file_message = approval_manage.otp_upload_manage.message
                download_type = 'otp'
            else: #ゲストアップロード
                first_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=approval_manage.guest_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=approval_manage.guest_upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.otp_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.guest_upload_manage
                file_title = approval_manage.guest_upload_manage.title
                file_message = approval_manage.guest_upload_manage.message
                download_type = 'guest'
                
            #   通知定義おわり

            # ログインユーザーが一次承認者の場合
            if first_approver:
                # ステータスを更新
                approval_manage.approval_status = 2
                approval_manage.approval_date = datetime.now()

                # 再申請フラグがTrueの場合はFalseに変更
                if approval_manage.is_reapplication_flg:
                    approval_manage.is_reapplication_flg = False
                approval_manage.save()
                
                # 第一承認者として設定されているトータルユーザーの数
                first_approval_manage_count = ""
                first_approval_manage_count = first_approval_manages.count()           
                # 第一承認ステータス
                first_approval_manage_status_list = []
                for first_approval_manage in first_approval_manages:
                    # ステータスをリストに追加
                    first_approval_manage_status_list.append(first_approval_manage.approval_status) 
                
                ######################################################通知　自分が第一承認者のなかで最終承認者
                ################### 第一承認者として設定されているトータルユーザーの数と現在一次承認済みの数
                if (first_approval_manage_count == first_approval_manage_status_list.count(2)): 
                    ##############第二承認者がいる場合----------第二承認者に承認依頼通知
                    ##第二承認者トータル取得
                    second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)#会社で指名されている固定の第一承認者
                    print('ファーストアプロ―バル222ステータス２',second_approvers)   

                    if second_approvers: #第二承認者いる
                        # status変更！
                        print("----------------- 一次承認済み")
                        upload_manage.application_status = 3 # 一次承認済み
                        upload_manage.save()
                        # 通知用情報取得
                        second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))#first_approversから第一承認者のユーザーIDだけのリストになっている
                        #第二承認者メールリスト
                        second_mails = []
                        for user in second_approver_list_raw_1:
                            s_user = User.objects.get(pk=user)
                            second_mails.append(s_user.email)
                        print('二次承認者いる',second_mails)
                        ###################　Notification通知用  ～の承認が申請されました
                        #送信先 email
                        emailList_db = ','.join(second_mails)#str型
                        emailList_for = list(second_mails)#list型
                        #タイトル
                        # Notice_title = "二次承認が依頼されました。"
                        Notice_title = create_user.display_name + "さんが" + file_title + "の承認を依頼しました。"
                        # #メッセージ
                        Notice_message = file_message

                        ###通知テーブル登録
                        Notification.objects.create(service="FileUP!",category="承認依頼",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

                        # #メール送信
                        current_site = get_current_site(self.request)
                        domain = current_site.domain
                        # download_type = 'normal'

                        tupleMessage = []
                        for email in emailList_for:
                            e_user = User.objects.filter(email=email).first()
                            
                            if e_user:
                                e_send = e_user.is_send_mail

                            if e_user and e_send == True or not e_user:
                                context = {
                                    'protocol': 'https' if self.request.is_secure() else 'http',
                                    'domain': domain,
                                    'download_type': download_type,
                                    #送信者
                                    'user_last_name':create_user.display_name,
                                }
                                subject_template = get_template('draganddrop/mail_template/approval_request_subject.txt')
                                subject = subject_template.render(context)

                                message_template = get_template('draganddrop/mail_template/approval_request.txt')
                                message = message_template.render(context)
                                from_email = settings.EMAIL_HOST_USER#CL側のメアド
                                recipient_list = [email]#受信者リスト
                                
                                message1 = (
                                    subject,
                                    message,
                                    from_email,
                                    recipient_list,
                                )
                                messageList = list(message1)
                                tupleMessage.insert(-1,messageList)

                        send_mass_mail(tupleMessage)
                        ##################Notification通知用終了       
                    else: ##################################第二承認者なし
                        # status変更！
                        print("----------------- 一次承認済み")
                        upload_manage.application_status = 3 # 一次承認済み
                        upload_manage.save()
                        ################################受信者にファイル受信通知
                        ###################　Notification通知用  ～を受信しました
                        #送信先取得,アドレス帳＆直接入力
                        dest_user =  upload_manage.dest_user.values_list('email', flat=True)
                        dest_user_list = list(dest_user)
                        #送信先グループ取得　OTPとかにも対応  value_listなし<QuerySet [<Group: aaa>]>→value_listあり<QuerySet ['aaa']>
                        dest_group = upload_manage.dest_user_group.values_list('group_name', flat=True)
                        dest_group_list = list(dest_group)
                        #送信先　直接入力＆アドレス帳＆グループ list型
                        dest_users = dest_user_list + dest_group_list
                        # ↑の('')を省くため文字列に変換
                        dest_users = ' '.join(dest_users)
                        #送信先 email
                        emailList_db = ','.join(dest_user_list)
                        #タイトル
                        Notice_title = create_user.display_name + "さんが" + file_title + "を共有しました。"
                        #メッセージ
                        Notice_message = upload_manage.message
                        #グループemaillist作成
                        group_email = []
                        for group in dest_group_list:
                            qs = Address.objects.filter(group__group_name=group)
                            for user in qs:
                                email = user.email
                                group_email.append(email)
                        group_email_db = ','.join(group_email)
                        emailList_for = list(dict.fromkeys(dest_user_list + group_email)) #list型
                        emailList_db = emailList_db + ',' + group_email_db #str型
                        ###通知テーブル登録
                        Notification.objects.create(service="FileUP!",category="受信通知",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)
                        #メール送信
                        current_site = get_current_site(self.request)
                        domain = current_site.domain

                        tupleMessage = []
                        for email in emailList_for:
                            e_user = User.objects.filter(email=email).first()
                            if e_user:
                                e_send = e_user.is_send_mail
                            if e_user and e_send == True or not e_user:
                                if approval_upload_method == "1":
                                    context = {
                                        'protocol': 'https' if self.request.is_secure() else 'http',
                                        'domain': domain,
                                        'download_type': download_type,
                                        #送信者
                                        'user_last_name':create_user.display_name,
                                    }
                                else:
                                    url = upload_manage.url
                                    context = {
                                        'protocol': 'https' if self.request.is_secure() else 'http',
                                        'domain': domain,
                                        'download_type': download_type,
                                        'url': url,
                                        #送信者
                                        'user_last_name':create_user.display_name,
                                    }
                                subject_template = get_template('draganddrop/mail_template/subject.txt')
                                subject = subject_template.render(context)
                                message_template = get_template('draganddrop/mail_template/message.txt')
                                message = message_template.render(context)
                                from_email = settings.EMAIL_HOST_USER#CL側のメアド
                                recipient_list = [email]#受信者リスト
                                message1 = (
                                    subject,
                                    message,
                                    from_email,
                                    recipient_list,
                                )
                                messageList = list(message1)
                                tupleMessage.insert(-1,messageList)
                        send_mass_mail(tupleMessage)
                        ##################Notification通知用終了
                        ##############送信者に承認完了した通知
                        ###################　Notification通知用  ～が承認されました
                        #送信先 email
                        emailList_db = create_user.email#str型
                        emailList_for = create_user.email#list型
                        #タイトル
                        # Notice_title = "二次承認が依頼されました。"
                        Notice_title =  file_title + "が承認されました。"
                        # #メッセージ
                        Notice_message = file_message
                        ###通知テーブル登録
                        Notification.objects.create(service="FileUP!",category="承認完了",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)
                        # #メール送信
                        current_site = get_current_site(self.request)
                        domain = current_site.domain

                        tupleMessage = []
                        # for email in emailList_for:
                        email = emailList_for
                        e_user = User.objects.filter(email=email).first()
                        print('承認メールきてる',email)
                        if e_user:
                            e_send = e_user.is_send_mail
                        if e_user and e_send == True or not e_user:
                            context = {
                                'protocol': 'https' if self.request.is_secure() else 'http',
                                'domain': domain,
                                # 'download_type': download_type,
                                #送信者
                                'user_last_name':create_user.display_name,
                            }
                            subject_template = get_template('draganddrop/mail_template/approval_done_subject.txt')
                            subject = subject_template.render(context)
                            message_template = get_template('draganddrop/mail_template/approval_done.txt')
                            message = message_template.render(context)
                            from_email = settings.EMAIL_HOST_USER#CL側のメアド
                            recipient_list = [email]#受信者リスト
                            message1 = (
                                subject,
                                message,
                                from_email,
                                recipient_list,
                            )
                            messageList = list(message1)
                            tupleMessage.insert(-1,messageList)
                        send_mail(subject, message, from_email, recipient_list)
                        ##################Notification通知用終了                                   
                #######ログのセーブ
                if approval_upload_method == "1":
                    # print("-------------- 承認履歴 通常アップロード")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.upload_manage.is_reapplied_flg:
                        approval_manage.upload_manage.is_reapplied_flg = False
                        approval_manage.upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        upload_manage = approval_manage.upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 2,# 一次承認
                        message = approve_comment,
                        manage_id = approval_manage.upload_manage.pk
                    )
                elif approval_upload_method == "2":
                    # print("-------------- 承認履歴 URL共有")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.url_upload_manage.is_reapplied_flg:
                        approval_manage.url_upload_manage.is_reapplied_flg = False
                        approval_manage.url_upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        url_upload_manage = approval_manage.url_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 2,# 一次承認
                        message = approve_comment,
                        manage_id = approval_manage.url_upload_manage.pk
                    )
                elif approval_upload_method == "3":
                    print("-------------- 承認履歴 OPT")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.otp_upload_manage.is_reapplied_flg:
                        approval_manage.otp_upload_manage.is_reapplied_flg = False
                        approval_manage.otp_upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        otp_upload_manage = approval_manage.otp_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 2,# 一次承認
                        message = approve_comment,
                        manage_id = approval_manage.otp_upload_manage.pk
                    )
                else:
                    print("-------------- 承認履歴 ゲスト")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.guest_upload_manage.is_reapplied_flg:
                        approval_manage.guest_upload_manage.is_reapplied_flg = False
                        approval_manage.guest_upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        guest_upload_manage = approval_manage.guest_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 2,# 一次承認
                        message = approve_comment,
                        manage_id = approval_manage.guest_upload_manage.pk
                    )

                approval_log.save()

            # ログインユーザーが二次承認者
            else:
                # ステータスを更新
                approval_manage.approval_status = 3
                approval_manage.approval_date = datetime.now()

                # 再申請フラグがTrueの場合はFalseに変更
                if approval_manage.is_reapplication_flg:
                    approval_manage.is_reapplication_flg = False
                approval_manage.save()

                # 第二承認者として設定されているトータルユーザーの数
                second_approval_manage_count = ""
                second_approval_manage_count = second_approval_manages.count()
                # 第二承認ステータス
                second_approval_manage_status_list = []
                for second_approval_manage in second_approval_manages:
                    # ステータスをリストに追加
                    second_approval_manage_status_list.append(second_approval_manage.approval_status)


                if approval_upload_method == "1":
                    # print("-------------- 承認履歴 通常アップロード")
                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.upload_manage.is_reapplied_flg:
                        approval_manage.upload_manage.is_reapplied_flg = False
                        approval_manage.upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        upload_manage = approval_manage.upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 3,# 最終承認
                        message = approve_comment,
                        manage_id = approval_manage.upload_manage.pk
                    )
                elif approval_upload_method == "2":
                    # print("-------------- 承認履歴 URL共有")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.url_upload_manage.is_reapplied_flg:
                        approval_manage.url_upload_manage.is_reapplied_flg = False
                        approval_manage.url_upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        url_upload_manage = approval_manage.url_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 3,# 最終承認
                        message = approve_comment,
                        manage_id = approval_manage.url_upload_manage.pk
                    )
                elif approval_upload_method == "3":
                    print("-------------- 承認履歴 OPT")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.otp_upload_manage.is_reapplied_flg:
                        approval_manage.otp_upload_manage.is_reapplied_flg = False
                        approval_manage.otp_upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        otp_upload_manage = approval_manage.otp_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 3,# 最終承認
                        message = approve_comment,
                        manage_id = approval_manage.otp_upload_manage.pk
                    )
                else:
                    print("-------------- 承認履歴 ゲスト")

                    # 再申請済みフラグがTrueの場合はFalseに変更
                    if approval_manage.guest_upload_manage.is_reapplied_flg:
                        approval_manage.guest_upload_manage.is_reapplied_flg = False
                        approval_manage.guest_upload_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        guest_upload_manage = approval_manage.guest_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 3,# 最終承認
                        message = approve_comment,
                        manage_id = approval_manage.guest_upload_manage.pk
                    )
                approval_log.save()


                ######################################################自分が第二の最終承認者
                ################### 第二承認者として設定されているトータルユーザーの数と現在二次承認済みの数
                if (second_approval_manage_count == second_approval_manage_status_list.count(2)):
                    ########status変更！！
                    upload_manage.application_status = 5 # 最終承認済み
                    upload_manage.save()
                    
                    ################################受信者にファイル受信通知
                    ###################　Notification通知用  ～を受信しました 
                    #送信先取得,アドレス帳＆直接入力
                    dest_user =  upload_manage.dest_user.values_list('email', flat=True)
                    dest_user_list = list(dest_user)
                    #送信先グループ取得　OTPとかにも対応  value_listなし<QuerySet [<Group: aaa>]>→value_listあり<QuerySet ['aaa']>
                    dest_group = upload_manage.dest_user_group.values_list('group_name', flat=True)
                    dest_group_list = list(dest_group)
                    #送信先　直接入力＆アドレス帳＆グループ list型
                    dest_users = dest_user_list + dest_group_list
                    # ↑の('')を省くため文字列に変換
                    dest_users = ' '.join(dest_users)
                    #送信先 email
                    emailList_db = ','.join(dest_user_list)
                    # emailList_db = ','.join(dest_user_list)
                    #タイトル
                    Notice_title = create_user.display_name + "さんが" + file_title + "を共有しました。"
                    #メッセージ
                    Notice_message = upload_manage.message
                    #グループemaillist作成
                    group_email = []
                    for group in dest_group_list:
                        qs = Address.objects.filter(group__group_name=group)
                        for user in qs:
                            email = user.email
                            group_email.append(email)
                    group_email_db = ','.join(group_email)
                    emailList_for = list(dict.fromkeys(dest_user_list + group_email)) #list型
                    emailList_db = emailList_db + ',' + group_email_db #str型

                    ###通知テーブル登録
                    Notification.objects.create(service="FileUP!",category="受信通知",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

                    #メール送信
                    current_site = get_current_site(self.request)
                    domain = current_site.domain

                    tupleMessage = []
                    for email in emailList_for:
                        e_user = User.objects.filter(email=email).first()
                        
                        if e_user:
                            e_send = e_user.is_send_mail

                        if e_user and e_send == True or not e_user:
                            if approval_upload_method == "1":
                                context = {
                                    'protocol': 'https' if self.request.is_secure() else 'http',
                                    'domain': domain,
                                    'download_type': download_type,
                                    #送信者
                                    'user_last_name':create_user.display_name,
                                }
                            else:
                                url = upload_manage.url
                                context = {
                                    'protocol': 'https' if self.request.is_secure() else 'http',
                                    'domain': domain,
                                    'download_type': download_type,
                                    'url': url,
                                    #送信者
                                    'user_last_name':create_user.display_name,
                                }
                            subject_template = get_template('draganddrop/mail_template/subject.txt')
                            subject = subject_template.render(context)

                            message_template = get_template('draganddrop/mail_template/message.txt')
                            message = message_template.render(context)
                            from_email = settings.EMAIL_HOST_USER#CL側のメアド
                            recipient_list = [email]#受信者リスト
                            
                            message1 = (
                                subject,
                                message,
                                from_email,
                                recipient_list,
                            )
                            messageList = list(message1)
                            tupleMessage.insert(-1,messageList)

                    send_mass_mail(tupleMessage)
                    ##################Notification通知用終了

                    ##############送信者に承認完了した通知
                    ###################　Notification通知用  ～が承認されました
                    #送信先 email
                    emailList_db = create_user.email#str型
                    emailList_for = create_user.email#list型
                    #タイトル
                    # Notice_title = "二次承認が依頼されました。"
                    Notice_title =  file_title + "が承認されました。"
                    # #メッセージ
                    Notice_message = file_message

                    ###通知テーブル登録
                    Notification.objects.create(service="FileUP!",category="承認完了",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

                    # #メール送信
                    current_site = get_current_site(self.request)
                    domain = current_site.domain

                    tupleMessage = []
                    # for email in emailList_for:
                    email = emailList_for
                    e_user = User.objects.filter(email=email).first()
                    print('承認メールきてる',email)
                    if e_user:
                        e_send = e_user.is_send_mail

                    if e_user and e_send == True or not e_user:
                        context = {
                            'protocol': 'https' if self.request.is_secure() else 'http',
                            'domain': domain,
                            #送信者
                            'user_last_name':create_user.display_name,
                        }
                        subject_template = get_template('draganddrop/mail_template/approval_done_subject.txt')
                        subject = subject_template.render(context)

                        message_template = get_template('draganddrop/mail_template/approval_done.txt')
                        message = message_template.render(context)
                        from_email = settings.EMAIL_HOST_USER#CL側のメアド
                        recipient_list = [email]#受信者リスト
                        # recipient_list = [email]#受信者リスト
                        
                        message1 = (
                            subject,
                            message,
                            from_email,
                            recipient_list,
                        )
                        messageList = list(message1)
                        tupleMessage.insert(-1,messageList)
                    send_mail(subject, message, from_email, recipient_list)
                    ##################Notification通知用終了

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
差戻し
"""
class DeclineApplicationView(View):

    def post(self, request, *args, **kwargs):
        print("----------------- 差し戻しView")

        try:
            approval_manage_id = request.POST.get('approval_manage_id')

            returned_comment = request.POST.get('returned_comment')

            approval_upload_method = request.POST.get('approval_upload_method')

            # ログインしているユーザーのApprovalManageのレコードを取得
            approval_manage = ApprovalManage.objects.filter(id=approval_manage_id).first()

            # ステータス
            approval_manage.approval_status = 4

            # 差戻し日時
            approval_manage.returned_date = datetime.now()

            approval_manage.save()
            ###########################################################通知用定義
            # 一次承認者に設定されているユーザーを取得
            first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)#会社で指名されている固定の第一承認者
            first_approver_list = []
            first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))#first_approversから第一承認者のユーザーIDだけのリストになっている
            # IDをstrに直してリストに追加
            for first_approver_uuid_1 in first_approver_list_raw_1:
                first_approver_uuid_string_1 = str(first_approver_uuid_1)
                first_approver_list.append(first_approver_uuid_string_1)

            # 二次承認者に設定されているユーザーを取得
            second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
            second_approver_list = []
            second_approver_list_raw_1 = list(second_approvers.values_list('second_approver', flat=True))
            # IDをstrに直してリストに追加
            for second_approver_uuid_1 in second_approver_list_raw_1:
                second_approver_uuid_string_1 = str(second_approver_uuid_1)
                second_approver_list.append(second_approver_uuid_string_1)
            
            if approval_upload_method == "1":#通常アップロード
                # UploadManageに紐づく一次承認者のApprovalManageを取得
                first_approval_manages = ApprovalManage.objects.filter(upload_manage=approval_manage.upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(upload_manage=approval_manage.upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.upload_manage
                file_title = approval_manage.upload_manage.title
                file_message = approval_manage.upload_manage.message
            elif approval_upload_method == "2": # URL共有
                first_approval_manages = ApprovalManage.objects.filter(url_upload_manage=approval_manage.url_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(url_upload_manage=approval_manage.url_upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.url_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.url_upload_manage
                file_title = approval_manage.url_upload_manage.title
                file_message = approval_manage.url_upload_manage.message
            elif approval_upload_method == "3": # OTP共有
                first_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=approval_manage.otp_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=approval_manage.otp_upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.otp_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.otp_upload_manage
                file_title = approval_manage.otp_upload_manage.title
                file_message = approval_manage.otp_upload_manage.message
            else: #ゲストアップロード
                first_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=approval_manage.guest_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=approval_manage.guest_upload_manage, second_approver__in=first_approver_list)
                create_user_id = approval_manage.guest_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = approval_manage.guest_upload_manage
                file_title = approval_manage.guest_upload_manage.title
                file_message = approval_manage.guest_upload_manage.message
            #   通知定義おわり
                
            #############status変更！
            upload_manage.application_status = 7 # 差戻し
            upload_manage.save()
            
            # ログインユーザーが一次承認者の場合
            if approval_manage.first_approver:
                # print("-------------- 一次承認者")
                ##############送信者に差し戻された通知
                ###################　Notification通知用  ～が差し戻されました
                #送信先 email
                emailList_db = create_user.email#str型
                emailList_for = create_user.email#list型
                #タイトル
                # Notice_title = "二次承認が依頼されました。"
                Notice_title =  file_title + "が差し戻されました。"
                # #メッセージ
                Notice_message = file_message

                ###通知テーブル登録
                Notification.objects.create(service="FileUP!",category="差し戻し",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

                # #メール送信
                current_site = get_current_site(self.request)
                domain = current_site.domain
                download_type = 'normal'

                tupleMessage = []
                # for email in emailList_for:
                email = emailList_for
                e_user = User.objects.filter(email=email).first()
                print('承認メールきてる',email)
                if e_user:
                    e_send = e_user.is_send_mail

                if e_user and e_send == True or not e_user:
                    context = {
                        'protocol': 'https' if self.request.is_secure() else 'http',
                        'domain': domain,
                        'download_type': download_type,
                        #送信者
                        'user_last_name':create_user.display_name,
                    }
                    subject_template = get_template('draganddrop/mail_template/decline_application_subject.txt')
                    subject = subject_template.render(context)

                    message_template = get_template('draganddrop/mail_template/decline_application.txt')
                    message = message_template.render(context)
                    from_email = settings.EMAIL_HOST_USER#CL側のメアド
                    recipient_list = [email]#受信者リスト
                    # recipient_list = [email]#受信者リスト
                    
                    message1 = (
                        subject,
                        message,
                        from_email,
                        recipient_list,
                    )
                    messageList = list(message1)
                    tupleMessage.insert(-1,messageList)
                # send_mass_mail(tupleMessage)
                send_mail(subject, message, from_email, recipient_list)
                ##################Notification通知用終了
                # 承認履歴を残す
                if approval_upload_method == "1":
                    # print("-------------- 承認履歴 通常アップロード")
                    approval_log = ApprovalLog.objects.create(
                        upload_manage = approval_manage.upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.upload_manage.pk
                    )
                elif approval_upload_method == "2":
                    # print("-------------- 承認履歴 URL共有")
                    approval_log = ApprovalLog.objects.create(
                        url_upload_manage = approval_manage.url_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.url_upload_manage.pk
                    )
                elif approval_upload_method == "3":
                    # print("-------------- 承認履歴 OPT共有")
                    approval_log = ApprovalLog.objects.create(
                        otp_upload_manage = approval_manage.otp_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.otp_upload_manage.pk
                    )
                else:
                    # print("-------------- 承認履歴 ゲストアップロード")
                    approval_log = ApprovalLog.objects.create(
                        guest_upload_manage = approval_manage.guest_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 1,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.guest_upload_manage.pk
                    )

            # 二次承認者
            elif approval_manage.second_approver:
                # print("-------------- 二次承認者")
                ##############送信者に差し戻された通知
                ###################　Notification通知用  ～が差し戻されました
                #送信先 email
                emailList_db = create_user.email#str型
                emailList_for = create_user.email#list型
                #タイトル
                # Notice_title = "二次承認が依頼されました。"
                Notice_title =  file_title + "が差し戻されました。"
                # #メッセージ
                Notice_message = file_message

                ###通知テーブル登録
                Notification.objects.create(service="FileUP!",category="差し戻し",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

                # #メール送信
                current_site = get_current_site(self.request)
                domain = current_site.domain
                download_type = 'normal'

                tupleMessage = []
                # for email in emailList_for:
                email = emailList_for
                e_user = User.objects.filter(email=email).first()
                print('承認メールきてる',email)
                if e_user:
                    e_send = e_user.is_send_mail

                if e_user and e_send == True or not e_user:
                    context = {
                        'protocol': 'https' if self.request.is_secure() else 'http',
                        'domain': domain,
                        'download_type': download_type,
                        #送信者
                        'user_last_name':create_user.display_name,
                    }
                    subject_template = get_template('draganddrop/mail_template/decline_application_subject.txt')
                    subject = subject_template.render(context)

                    message_template = get_template('draganddrop/mail_template/decline_application.txt')
                    message = message_template.render(context)
                    from_email = settings.EMAIL_HOST_USER#CL側のメアド
                    recipient_list = [email]#受信者リスト
                    # recipient_list = [email]#受信者リスト
                    
                    message1 = (
                        subject,
                        message,
                        from_email,
                        recipient_list,
                    )
                    messageList = list(message1)
                    tupleMessage.insert(-1,messageList)
                # send_mass_mail(tupleMessage)
                send_mail(subject, message, from_email, recipient_list)
                ##################Notification通知用終了
                if approval_upload_method == "1":
                    # print("-------------- 承認履歴 通常アップロード")
                    approval_log = ApprovalLog.objects.create(
                        upload_manage = approval_manage.upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.upload_manage.pk
                    )
                elif approval_upload_method == "2":
                    # print("-------------- 承認履歴 URL共有")
                    approval_log = ApprovalLog.objects.create(
                        url_upload_manage = approval_manage.url_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.url_upload_manage.pk
                    )
                elif approval_upload_method == "3":
                    # print("-------------- 承認履歴 OPT共有")
                    approval_log = ApprovalLog.objects.create(
                        otp_upload_manage = approval_manage.otp_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.otp_upload_manage.pk
                    )
                else:
                    # print("-------------- 承認履歴 ゲストアップロード")
                    approval_log = ApprovalLog.objects.create(
                        guest_upload_manage = approval_manage.guest_upload_manage,
                        approval_operation_user = self.request.user.id,
                        approval_operation_user_position = 2,
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date = datetime.now(),
                        approval_operation_content = 4,
                        message = returned_comment,
                        manage_id = approval_manage.guest_upload_manage.pk
                    )
            else:
                print("------------------- 差戻 else")

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


"""
再申請
"""
class ReapplicationView(View):

    def post(self, request, *args, **kwargs):
        print("----------------- 再申請View")

        try:
            upload_manage_pk = request.POST.get('upload_manage_pk')
            # print("----------------- upload_manage_pk", upload_manage_pk)
            reapplication_comment = request.POST.get('reapplication_comment')
            upload_method = request.POST.get('upload_method')
            # print("----------------- upload_method", upload_method)
            ###########################################################通知用定義
            # 一次承認者に設定されているユーザーを取得
            first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)#会社で指名されている固定の第一承認者
            first_approver_list = []
            first_approver_list_raw_1 = list(first_approvers.values_list('first_approver', flat=True))#first_approversから第一承認者のユーザーIDだけのリストになっている
            # IDをstrに直してリストに追加
            for first_approver_uuid_1 in first_approver_list_raw_1:
                first_approver_uuid_string_1 = str(first_approver_uuid_1)
                first_approver_list.append(first_approver_uuid_string_1)
            #通知用メールアドレスリスト
            first_approver_emaillist = []
            for first_approver in first_approvers:
                #通知用メールアドレス取得
                first_id = first_approver.first_approver
                first_user = User.objects.get(id=first_id)
                first_mail = first_user.email
                first_approver_emaillist.append(first_mail)
            if upload_method == "1":
                # print("-------------- 承認履歴 通常アップロード")

                upload_manage = UploadManage.objects.filter(id=upload_manage_pk).first()

                # 再申請済みフラグをTrueに変更
                upload_manage.is_reapplied_flg = True
                upload_manage.save()
                # UploadManageに紐づく一次承認者のApprovalManageを取得
                first_approval_manages = ApprovalManage.objects.filter(upload_manage=upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(upload_manage=upload_manage, second_approver__in=first_approver_list)
                create_user_id = upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                file_title = upload_manage.title
                file_message = upload_manage.message
                # 承認履歴を残す
                approval_log = ApprovalLog.objects.create(
                    upload_manage = upload_manage,
                    approval_operation_user = self.request.user.id,
                    approval_operation_user_position = 3,
                    approval_operation_user_company_id = self.request.user.company.id,
                    approval_operation_date = datetime.now(),
                    approval_operation_content = 6,
                    message = reapplication_comment,
                    manage_id = upload_manage.pk
                )
            elif upload_method == "2":
                # print("-------------- 承認履歴 URL共有")

                url_upload_manage = UrlUploadManage.objects.filter(id=upload_manage_pk).first()

                # 再申請済みフラグをTrueに変更
                url_upload_manage.is_reapplied_flg = True
                url_upload_manage.save()
                first_approval_manages = ApprovalManage.objects.filter(url_upload_manage=url_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(url_upload_manage=url_upload_manage, second_approver__in=first_approver_list)
                create_user_id = url_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = url_upload_manage
                file_title = url_upload_manage.title
                file_message = url_upload_manage.message
                # 承認履歴を残す
                approval_log = ApprovalLog.objects.create(
                    url_upload_manage = url_upload_manage,
                    approval_operation_user = self.request.user.id,
                    approval_operation_user_position = 3,
                    approval_operation_user_company_id = self.request.user.company.id,
                    approval_operation_date = datetime.now(),
                    approval_operation_content = 6,
                    message = reapplication_comment,
                    manage_id = url_upload_manage.pk
                )
            elif upload_method == "3":
                # print("-------------- 承認履歴 OPT共有")

                otp_upload_manage = OTPUploadManage.objects.filter(id=upload_manage_pk).first()

                # 再申請済みフラグをTrueに変更
                otp_upload_manage.is_reapplied_flg = True
                otp_upload_manage.save()
                first_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=otp_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(otp_upload_manage=otp_upload_manage, second_approver__in=first_approver_list)
                create_user_id = otp_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = otp_upload_manage
                file_title = otp_upload_manage.title
                file_message = otp_upload_manage.message
                # 承認履歴を残す
                approval_log = ApprovalLog.objects.create(
                    otp_upload_manage = otp_upload_manage,
                    approval_operation_user = self.request.user.id,
                    approval_operation_user_position = 3,
                    approval_operation_user_company_id = self.request.user.company.id,
                    approval_operation_date = datetime.now(),
                    approval_operation_content = 6,
                    message = reapplication_comment,
                    manage_id = otp_upload_manage.pk
                )
            else:
                # print("-------------- 承認履歴 ゲストアップロー")

                guest_upload_manage = GuestUploadManage.objects.filter(id=upload_manage_pk).first()

                # 再申請済みフラグをTrueに変更
                guest_upload_manage.is_reapplied_flg = True
                guest_upload_manage.save()
                first_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=guest_upload_manage, first_approver__in=first_approver_list)
                second_approval_manages = ApprovalManage.objects.filter(guest_upload_manage=guest_upload_manage, second_approver__in=first_approver_list)
                create_user_id = otp_upload_manage.created_user
                create_user = User.objects.get(pk=create_user_id)
                upload_manage = guest_upload_manage
                file_title = guest_upload_manage.title
                file_message = guest_upload_manage.message
                # 承認履歴を残す
                approval_log = ApprovalLog.objects.create(
                    guest_upload_manage = guest_upload_manage,
                    approval_operation_user = self.request.user.id,
                    approval_operation_user_position = 3,
                    approval_operation_user_company_id = self.request.user.company.id,
                    approval_operation_date = datetime.now(),
                    approval_operation_content = 6,
                    message = reapplication_comment,
                    manage_id = guest_upload_manage.pk
                )

            approval_log.save()
            ###################　Notification通知用  ～の承認が申請されました
            #送信先 email
            emailList_db = ','.join(first_approver_emaillist)#str型
            emailList_for = list(first_approver_emaillist)#list型
            print('承認通知第一承認mail',emailList_for)
            #タイトル
            Notice_title = create_user.display_name + "さんが" + file_title + "の承認を依頼しました。"
            #メッセージ
            Notice_message = upload_manage.message
            print('承認通知たいとる',Notice_title)
            print('承認通知めっせーじ',Notice_message)

            ###通知テーブル登録
            Notification.objects.create(service="FileUP!",category="承認依頼",sender=create_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

            #メール送信
            current_site = get_current_site(self.request)
            domain = current_site.domain
            download_type = 'normal'

            tupleMessage = []
            for email in emailList_for:
                e_user = User.objects.filter(email=email).first()
                
                if e_user:
                    e_send = e_user.is_send_mail

                if e_user and e_send == True or not e_user:
                    context = {
                        'protocol': 'https' if self.request.is_secure() else 'http',
                        'domain': domain,
                        'download_type': download_type,
                        #送信者
                        'user_last_name':self.request.user.last_name,
                        'user_first_name':self.request.user.first_name,
                    }
                    subject_template = get_template('draganddrop/mail_template/approval_request_subject.txt')
                    subject = subject_template.render(context)

                    message_template = get_template('draganddrop/mail_template/approval_request.txt')
                    message = message_template.render(context)
                    from_email = settings.EMAIL_HOST_USER#CL側のメアド
                    recipient_list = [email]#受信者リスト
                    
                    message1 = (
                        subject,
                        message,
                        from_email,
                        recipient_list,
                    )
                    messageList = list(message1)
                    tupleMessage.insert(-1,messageList)

            send_mass_mail(tupleMessage)
            ##################Notification通知用終了
            
            # 差戻しを行ったユーザーのApprovalManageを取得
            approval_manage_status_returned = ApprovalManage.objects.filter(manage_id=upload_manage_pk, approval_status=4).first()
            # print("---------------approval_manage_status_returned", approval_manage_status_returned)

            # 再申請済みフラグをTrueに変更
            approval_manage_status_returned.is_reapplication_flg = True
            approval_manage_status_returned.save()

            # メッセージを返す
            message = f'再申請しました'
            messages.success(self.request, message)

            # メッセージを生成してJSONで返す
            return JsonResponse({"status": "ok",
                                "message": "再申請しました",
                                })

        except Exception as e:
            print("ERROR", e) # 'e'の中にエラーの該当行が入る
            data = {}
            data['status'] = 'ng'
            data['message'] = '再申請に失敗しました'
            return JsonResponse(data)


"""
取り消し(削除) 通常アップロード
※UploadManageのDBデータは削除
"""
class ApprovalDeleteAjaxView(View,CommonView):

    def post(self, request,**kwargs):

        print('----------------- ApprovalDeleteAjaxView 取り消し(削除) 通常アップロード')

        # ダウンロードされたファイルが単体か複数か判断するための変数
        send_delete_id = request.POST.getlist('send_delete_id[]')# UploadManageのID
        send_delete_name = request.POST.get('send_delete_name')# ファイルのタイトル
        # print('----------------- send_delete_id', send_delete_id)
        # print('----------------- send_delete_name', send_delete_name)

        upload_manages = UploadManage.objects.filter(pk__in=send_delete_id)
        # print('----------------- upload_manages', upload_manages)


        try:
            for upload_manage in upload_manages:

                #download_tableのレコード数を取得
                number_of_download_table = Downloadtable.objects.filter(upload_manage=upload_manage).all().count()
                # print("----------------- number_of_download_table", number_of_download_table)

                # download_file_tableのレコード数を取得
                number_of_download_file_table = 0
                for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
                        number_of_download_file_table += int(downloadtable.downloadtable.all().count())

                files = upload_manage.file.all()
                # print("----------------- files", files)

                upload_manage_file_size = 0

                for file in files:
                    # 管理テーブルから合計サイズをマイナスするためサイズデータ抽出する
                    upload_manage_file_size = upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload

                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    # print("----------------- file_num", file_num)

                    if file_num == 1:
                        # 実ファイル名を文字列にデコード
                        file_path = urllib.parse.unquote(file.upload.url)
                        # ファイルパスを分割してファイル名だけ取得
                        file_name = file_path.split('/', 3)[3]
                        # パスを取得
                        path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                        # パスの存在確認
                        result = os.path.exists(path)
                        if result:
                            # 絶対パスでファイル実体を削除
                            os.remove(os.path.join(
                                settings.FULL_MEDIA_ROOT, file_name))

                    # DBの対象行を削除
                    file.delete()


                # ApprovalManageを削除
                approval_manages = ApprovalManage.objects.filter(upload_manage=upload_manage)
                approval_manages.delete()

                # ApprovalLogを削除
                approval_logs = ApprovalLog.objects.filter(upload_manage=upload_manage)
                approval_logs.delete()

                upload_manage.delete()

            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, number_of_download_table, number_of_download_file_table, upload_manage_file_size, 1)

            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)


"""
取り消し(削除) URL共有
※UploadManageのDBデータは削除
"""
class UrlApprovalDeleteAjaxView(View):

    def post(self, request):

        print('----------------- ApprovalDeleteAjaxView 取り消し(削除) URL共有')

        url_send_delete_id = request.POST.getlist('url_send_delete_id[]')
        url_send_delete_name = request.POST.get('url_send_delete_name')

        url_upload_manages = UrlUploadManage.objects.filter(pk__in=url_send_delete_id)

        try:
            for url_upload_manage in url_upload_manages:

                #download_tableのレコード数を取得
                number_of_url_download_table = UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all().count()

                # download_file_tableのレコード数を取得
                number_of_url_download_file_table = 0
                for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
                    number_of_url_download_file_table += int(urldownloadtable.url_download_table.all().count())

                # ファイルの実態が削除されていないデータのみ抽出する
                files = url_upload_manage.file.all()
                url_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするためサイズデータ抽出する
                    url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

                        # 実ファイル名を文字列にデコード
                        file_path = urllib.parse.unquote(file.upload.url)
                        # ファイルパスを分割してファイル名だけ取得
                        file_name = file_path.split('/', 3)[3]
                        # file_name = file_path.split('/', 2)[2]

                        # パスを取得
                        path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                        # パスの存在確認
                        result = os.path.exists(path)
                        if result:
                            # 絶対パスでファイル実体を削除
                            os.remove(os.path.join(
                                settings.FULL_MEDIA_ROOT, file_name))

                    # DBの対象行を削除
                    file.delete()

                # ApprovalManageを削除
                approval_manages = ApprovalManage.objects.filter(url_upload_manage=url_upload_manage)
                # print("------------------- approval_manages", approval_manages)
                approval_manages.delete()

                # ApprovalLogを削除
                approval_logs = ApprovalLog.objects.filter(url_upload_manage=url_upload_manage)
                # print("------------------- approval_logs", approval_logs)
                approval_logs.delete()

                url_upload_manage.delete()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, number_of_url_download_table, number_of_url_download_file_table, url_upload_manage_file_size, 2)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = url_send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)



"""
取り消し(削除) OTP共有
※UploadManageのDBデータは削除
"""

class OTPApprovalDeleteAjaxView(View):
    def post(self, request):

        otp_send_delete_id = request.POST.getlist('otp_send_delete_id[]')
        otp_send_delete_name = request.POST.get('otp_send_delete_name')
        otp_upload_manages = OTPUploadManage.objects.filter(pk__in=otp_send_delete_id)

        try:
            for otp_upload_manage in otp_upload_manages:

                #download_tableのレコード数を取得
                number_of_otp_download_table = OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all().count()

                # download_file_tableのレコード数を取得
                number_of_otp_download_file_table = 0
                for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
                    number_of_otp_download_file_table += int(otpdownloadtable.otp_download_table.all().count())

                # ファイルの実態が削除されていないデータのみ抽出する
                files = otp_upload_manage.file.all()
                otp_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするためサイズデータ抽出する
                    otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

                        # 実ファイル名を文字列にデコード
                        file_path = urllib.parse.unquote(file.upload.url)
                        # ファイルパスを分割してファイル名だけ取得
                        file_name = file_path.split('/', 3)[3]
                        # file_name = file_path.split('/', 2)[2]

                        # パスを取得
                        path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                        # パスの存在確認
                        result = os.path.exists(path)
                        if result:
                            # 絶対パスでファイル実体を削除
                            os.remove(os.path.join(
                                settings.FULL_MEDIA_ROOT, file_name))

                    # DBの対象行を削除
                    file.delete()

                # ApprovalManageを削除
                approval_manages = ApprovalManage.objects.filter(otp_upload_manage=otp_upload_manage)
                # print("------------------- approval_manages", approval_manages)
                approval_manages.delete()

                # ApprovalLogを削除
                approval_logs = ApprovalLog.objects.filter(otp_upload_manage=otp_upload_manage)
                # print("------------------- approval_logs", approval_logs)
                approval_logs.delete()

                otp_upload_manage.delete()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, number_of_otp_download_table, number_of_otp_download_file_table, otp_upload_manage_file_size, 3)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = otp_send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)


# """
# 取り消し(削除) ゲストアップロード
# ※UploadManageのDBデータは削除
# """
# class GuestApprovalDeleteAjaxView(View):
#     def post(self, request):
#         guest_delete_id = request.POST.get('guest_delete_id')
#         guest_delete_name = request.POST.get('guest_delete_name')
#         guest_upload_manage = GuestUploadManage.objects.filter(pk=guest_delete_id)

#         try:
#             guestdownloadtable = GuestUploadDownloadtable.objects.get(pk__exact=guest_delete_id)
#             guestdownloadtable.trash_flag = True
#             guestdownloadtable.save()

#             # ApprovalManageを削除
#             approval_manages = ApprovalManage.objects.filter(guest_upload_manage=guest_upload_manage)
#             # print("------------------- approval_manages", approval_manages)
#             approval_manages.delete()

#             # ApprovalLogを削除
#             approval_logs = ApprovalLog.objects.filter(guest_upload_manage=guest_upload_manage)
#             # print("------------------- approval_logs", approval_logs)
#             approval_logs.delete()

#             #メッセージを格納してJSONで返す
#             data = {}
#             data['message'] = guest_delete_name + 'を削除しました'
#             return JsonResponse(data)

#         except Exception as e:

#             #失敗時のメッセージを格納してJASONで返す
#             data = {}
#             data['message'] = '削除に失敗しました'
#             return JsonResponse(data)


"""
承認ルート設定画面
"""
class ApprovalRouteView(TemplateView, CommonView):
    template_name = 'draganddrop/ApprovalRouteView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


"""
グループ一覧画面
"""
class ApprovalGroupManagementView(ListView, CommonView):
    model = CustomGroup
    template_name = 'draganddrop/ApprovalGroupManagementView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        groups = CustomGroup.objects.filter(reg_user=self.request.user.id)
        context["groups"] = groups

        # user_custom_group_relations = UserCustomGroupRelation.objects.all()
        # context["user_custom_group_relations"] = user_custom_group_relations

        return context


"""
グループ作成
"""
class ApprovalGroupCreateView(CommonView, FormView):
    # フォームを変数にセット
    model = CustomGroup
    template_name = 'draganddrop/ApprovalGroupCreateView.html'
    form_class = CustomGroupForm

    # formに値を渡す
    def get_form_kwargs(self):
        # formにログインユーザーを渡す
        kwargs = super(ApprovalGroupCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        print("-------------- グループ作成")

        # グループに対してユーザーを紐づける
        group_user_qs = form.cleaned_data['group_user']
        group_name = form.cleaned_data['group_name']
        print("-------------- group_user_qs", group_user_qs)
        print("-------------- group_name", group_name)

        # CustomGroupモデルのnameフィールドにgroup_nameを保存
        custom_group, created = CustomGroup.objects.get_or_create(
            group_name = group_name,
            reg_user = self.request.user.id,
            reg_date = datetime.now(),
        )
        custom_group.save()

        group = CustomGroup.objects.filter(group_name=group_name).first()
        print("-------------- group", group)

        # UserCustomGroupRelationモデルのgroup_idフィールドにグループのid、group_userにgroup_user_qsを保存
        for group_user in group_user_qs:
            print("-------------- group_user", group_user)

            user_custom_group_relation, created = UserCustomGroupRelation.objects.get_or_create(
                group_id = group.id,
                group_user = group_user.id,
            )
            user_custom_group_relation.save()

        # メッセージを返す
        messages.success(self.request, "グループを作成しました。")

        return redirect('draganddrop:approval_group_management')


"""
グループ削除
"""
class ApprovalGroupDeleteView(DeleteView):
    model = CustomGroup
    template_name = 'draganddrop/ApprovalGroupManagementView.html'

    def get_success_url(self):
        # 削除対象のグループのIDを取得
        group_id = self.object.pk

        # 一致するグループを取得
        del_group = CustomGroup.objects.filter(pk=group_id).first()
        print("---------- del_group ---------", del_group)
        print("---------- del_group pk ---------", del_group.pk)

        del_users = UserCustomGroupRelation.objects.filter(group_id=del_group.id)
        print("---------- del_users ---------", del_users)

        # 削除するグループに所属しているユーザーのリストを作成
        # delete_user_list = []

        # # delete_user_list = list(del_users)
        # delete_user_list_raw = list(del_users.values_list('group_user', flat=True))
        # print("---------- delete_user_list ---------", delete_user_list_raw)#  [<UserCustomGroupRelation: UserCustomGroupRelation object (24)>, <UserCustomGroupRelation: UserCustomGroupRelation object (25)>]

        # # IDをstrに直してリストに追加
        # for group_user_uuid in delete_user_list_raw:
        #     group_user_uuid_string = str(group_user_uuid)
        #     delete_user_list.append(group_user_uuid_string)

        # 削除しないグループに所属するユーザーのリスト
        # not_del_users_list = []

        # グループが紐づいているトレーニングの情報を取得
        # trainings = TrainingRelation.objects.filter(group_id=del_group.pk)
        # print("---------- グループに紐づいているトレーニングを取得 ---------", trainings)# <QuerySet [<TrainingRelation: TrainingRelation object (177)>]>

        # if trainings:
        #     # トレーニングをリスト化
        #     training_list = []
        #     delete_training_list_raw = list(trainings.values_list('training_id', flat=True))
        #     print("---------- delete_training_list_raw ---------", delete_training_list_raw)# [UUID('66796700-1f36-4ad5-9fcf-1d216954049d'), UUID('f3986e94-53f4-4258-afb6-91b170d92698')]

        #     # IDをstrに直してリストに追加
        #     for training_uuid in delete_training_list_raw:
        #         training_uuid_string = str(training_uuid)
        #         training_list.append(training_uuid_string)
        #     print("---------- training_list ---------", training_list)# ['66796700-1f36-4ad5-9fcf-1d216954049d', 'f3986e94-53f4-4258-afb6-91b170d92698']

        #     # トレーニングに紐づいている削除対象のグループを除いたグループを取得する
        #     not_del_groups = TrainingRelation.objects.filter(training_id__in=training_list).exclude(group_id=group_id)
        #     print("---------- not_del_groups ---------", not_del_groups)# <QuerySet []>

        #     # グループに所属しているユーザーを取得
        #     for not_del_group in not_del_groups:

        #         users = UserCustomGroupRelation.objects.filter(group_id=not_del_group.group_id)
        #         print("---------- グループに所属しているユーザーを取得 ---------", users)# <QuerySet [<UserCustomGroupRelation: UserCustomGroupRelation object (24)>, <UserCustomGroupRelation: UserCustomGroupRelation object (25)>]>

        #         # 削除しないグループのユーザーをforで回して取り出す
        #         for not_del_users in users:
        #             print("---------- not_del_users ---------", not_del_users)# UserCustomGroupRelation object (47)
        #             # リストにユーザーを追加
        #             not_del_users_list.append(not_del_users.group_user)
        #             print("---------- not_del_users_list ---------", not_del_users_list)#  [<UserCustomGroupRelation: UserCustomGroupRelation object (47)>, <UserCustomGroupRelation: UserCustomGroupRelation object (48)>]

        #     # リストの中に共通するユーザーがいる場合
        #     if set(delete_user_list) & set(not_del_users_list):
        #         print("---------- 重複ユーザーがいます ---------")

        #         # 重複しているユーザーのリストを作成
        #         repetitive_user = set(delete_user_list) & set(not_del_users_list)
        #         repetitive_user_list = list(repetitive_user)
        #         print("---------- repetitive_user_list ---------", repetitive_user_list)# ['9a058d25-384d-43e1-9a26-c1a680c87ab4']

        #         # 重複ユーザーを除いたユーザーと一致するTrainingManageを取得
        #         user_training_manages_qs = TrainingManage.objects.filter(user__in=delete_user_list, training__in=training_list).exclude(user__in=repetitive_user_list)
        #         print("--------------- 重複ユーザーを除いた一致するユーザーのTrainingManageを取得(削除) --------------", user_training_manages_qs)

        #         # 重複ユーザーを除いたユーザーと一致するトグルボタンの展開データを取得
        #         user_folder_is_open_qs = FolderIsOpen.objects.filter(user_id__in=delete_user_list, training__in=training_list).exclude(user_id__in=repetitive_user_list)
        #         print("---------- user_folder_is_open_qs ---------", user_folder_is_open_qs)

        #     # TrainingManageを削除しない
        #     else:
        #         print("---------- 重複ユーザーはいません ---------")

        #         # ユーザーと一致するTrainingManageを取得
        #         user_training_manages_qs = TrainingManage.objects.filter(user__in=delete_user_list, training__in=training_list)
        #         print("---------- user_training_manages_qs ---------", user_training_manages_qs)

        #         # ユーザーと一致するトグルボタンの展開データを取得
        #         user_folder_is_open_qs = FolderIsOpen.objects.filter(user_id__in=delete_user_list, training__in=training_list)
        #         print("---------- user_folder_is_open_qs ---------", user_folder_is_open_qs)

        #     # 削除対象のユーザーと一致するPartsgManageを取得
        #     for user_training_manages in user_training_manages_qs:
        #         print("--------------- user_training_manages", user_training_manages)# TrainingManage object (509)
        #         user_parts_manages = user_training_manages.parts_manage.all()
        #         print("--------------- ユーザーのparts_manage", user_parts_manages)# <QuerySet [<PartsManage: PartsManage object (57)>]>
        #         # PartsgManageを削除
        #         user_parts_manages.delete()

        #     # TrainingManageを削除
        #     user_training_manages_qs.delete()

        #     # トグルボタンの展開データを削除
        #     user_folder_is_open_qs.delete()

        # UserCustomGroupRelationテーブルから該当する一行を削除
        del_group.delete()
        del_users.delete()

        # メッセージを返す
        messages.success(self.request, "グループを削除しました。")

        return reverse_lazy('draganddrop:approval_group_management')
