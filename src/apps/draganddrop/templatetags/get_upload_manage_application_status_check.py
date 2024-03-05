from django import template
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, UrlUploadManage,OTPUploadManage, ApprovalManage, FirstApproverRelation, SecondApproverRelation, ApprovalWorkflow
register = template.Library()

@register.filter
def get_upload_manage_application_status_check(value,upload_method):

    if upload_method == 1:
        upload_manage = UploadManage.objects.filter(id=value).first()
    elif upload_method == 2:
        upload_manage = UrlUploadManage.objects.filter(id=value).first()

    elif upload_method == 3:
        upload_manage = OTPUploadManage.objects.filter(id=value).first()

    else:
        print('guestと判断')
        result = 'OK'
    
    if upload_method == 1 or upload_method == 2 or upload_method == 3:
        user = User.objects.filter(id=upload_manage.created_user).first()

        """一次承認者"""
        first_approver = FirstApproverRelation.objects.filter(company_id=user.company.id).first()

        """二次承認者"""
        second_approver = SecondApproverRelation.objects.filter(company_id=user.company.id).first()

        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=user.company.id).first()
        # (1, '申請中'),ok
        # (2, '一次承認待ち'),
        # (3, '一次承認済み'),OK
        # (4, '最終承認待ち'),
        # (5, '最終承認済み'),OK
        # (6, 'キャンセル'),ok
        # (7, '差戻し'),ok
        # (8, '再申請')ok
        """ アップロード方法ごとにupload_manageのapplication_statusを取得して返す"""
        if approval_workflow.is_approval_workflow == 1:# 承認ワークフローを使用
            if upload_manage.application_status == 1:
                result = '1NG'
            elif  upload_manage.application_status == 7:
                result = '7NG'
            elif  upload_manage.application_status == 8:
                result = '1NG'
            elif  upload_manage.application_status == 6:
                result = '6NG'
            else:
                # 一次承認者と二次承認者が設定されている場合
                if first_approver and second_approver:
                    if upload_manage.application_status == 5 or upload_manage.application_status == 3:
                        result = 'OK'
                    else:
                        result = '1NG'

                # 一次承認者しか設定されていない場合
                else:
                    if upload_manage.application_status == 3 or upload_manage.application_status == 5:
                        result = 'OK'
                    else:
                        result = '1NG'
        else:# 承認ワークフローを使用しない
            result = 'OK'
    
    return result