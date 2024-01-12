from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, ApprovalManage, ApprovalLog
register = template.Library()


@register.filter
def get_approval_log(value):
    """ 承認履歴を取得"""
    # print("--------------- value", value)# アップロード1
    # print("--------------- user_approval_manage id", value.id)# 4f69524d-5d60-44c0-8bff-f5f360896487

    approval_manages = ApprovalManage.objects.filter(upload_mange=value)
    # print("--------------- approval_manages", approval_manages)

    approval_manage_list = []
    approval_manage_list_raw_1 = list(approval_manages.values_list('id', flat=True))

    # IDをstrに直してリストに追加
    for approval_manage_uuid_1 in approval_manage_list_raw_1:
        approval_manage_uuid_string_1 = str(approval_manage_uuid_1)
        approval_manage_list.append(approval_manage_uuid_string_1)

    approval_logs = ApprovalLog.objects.filter(approval_manage__in=approval_manage_list).order_by("approval_operation_date", "approval_operation_content")
    # print("--------------- approval_logs", approval_logs)

    return approval_logs
