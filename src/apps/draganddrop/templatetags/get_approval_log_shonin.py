from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, UrlUploadManage, OTPUploadManage, GuestUploadManage, ApprovalManage, ApprovalLog
register = template.Library()


@register.filter
def get_approval_log_shonin(value):
    """ 承認一覧 承認履歴を取得"""
    print("--------------- 承認一覧 承認履歴を取得 value", value)

    # 通常アップロード
    if value.upload_method == 1:
        # print("------------------------- 通常アップロード")

        upload_manages = UploadManage.objects.filter(id=value.manage_id)
        # print("--------------- upload_manages", upload_manages)

        upload_manage_list = []
        upload_manage_list_raw_1 = list(upload_manages.values_list('id', flat=True))

        # IDをstrに直してリストに追加
        for upload_manage_uuid_1 in upload_manage_list_raw_1:
            upload_manage_uuid_string_1 = str(upload_manage_uuid_1)
            upload_manage_list.append(upload_manage_uuid_string_1)

        approval_logs = ApprovalLog.objects.filter(upload_manage__in=upload_manage_list).order_by("approval_operation_date", "approval_operation_content")

    # URL共有
    elif value.upload_method == 2:
        # print("------------------------- URL共有")

        url_upload_manages = UrlUploadManage.objects.filter(id=value.manage_id)
        # print("--------------- upload_manages", upload_manages)

        url_upload_manage_list = []
        url_upload_manage_list_raw_1 = list(url_upload_manages.values_list('id', flat=True))

        # IDをstrに直してリストに追加
        for url_upload_manage_uuid_1 in url_upload_manage_list_raw_1:
            url_upload_manage_uuid_string_1 = str(url_upload_manage_uuid_1)
            url_upload_manage_list.append(url_upload_manage_uuid_string_1)

        approval_logs = ApprovalLog.objects.filter(url_upload_manage__in=url_upload_manage_list).order_by("approval_operation_date", "approval_operation_content")

    # OTP共有
    elif value.upload_method == 3:
        print("------------------------- OTP共有")

        otp_upload_manages = OTPUploadManage.objects.filter(id=value.manage_id)
        print("--------------- otp_upload_manages", otp_upload_manages)

        otp_upload_manage_list = []
        otp_upload_manage_list_raw_1 = list(otp_upload_manages.values_list('id', flat=True))

        # IDをstrに直してリストに追加
        for otp_upload_manage_uuid_1 in otp_upload_manage_list_raw_1:
            otp_upload_manage_uuid_string_1 = str(otp_upload_manage_uuid_1)
            otp_upload_manage_list.append(otp_upload_manage_uuid_string_1)

        approval_logs = ApprovalLog.objects.filter(otp_upload_manage__in=otp_upload_manage_list).order_by("approval_operation_date", "approval_operation_content")

    # ゲストアップロード
    else:
        # print("------------------------- ゲストアップロード")

        guest_upload_manages = GuestUploadManage.objects.filter(id=value.manage_id)
        # print("--------------- upload_manages", upload_manages)

        guest_upload_manage_list = []
        guest_upload_manage_list_raw_1 = list(guest_upload_manages.values_list('id', flat=True))

        # IDをstrに直してリストに追加
        for guest_upload_manage_uuid_1 in guest_upload_manage_list_raw_1:
            guest_upload_manage_uuid_string_1 = str(guest_upload_manage_uuid_1)
            guest_upload_manage_list.append(guest_upload_manage_uuid_string_1)

        approval_logs = ApprovalLog.objects.filter(guest_upload_manage__in=guest_upload_manage_list).order_by("approval_operation_date", "approval_operation_content")


    return approval_logs
