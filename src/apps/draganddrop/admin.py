from django.contrib import admin

from .models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage, ApprovalLog, UserCustomGroupRelation, CustomGroup
from .models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, Address,OperationLog
# from .models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage
from .models import OTPUploadManage, OTPDownloadtable, OTPDownloadFiletable, GuestUploadManage, GuestUploadDownloadtable, GuestUploadDownloadFiletable
from .models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, Address,OperationLog
from accounts.models import Notification,Read
# Register your models here.



class UploadManageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', '_file', '_dest_user', 'dest_user_mail1', 'dest_user_mail2', 'dest_user_mail3', 'dest_user_mail4', 'dest_user_mail5', 'dest_user_mail6', 'dest_user_mail7', 'dest_user_mail8', 'created_user',
                    'created_date', 'end_date', 'tmp_flag', 'file_del_flag', 'is_downloaded', 'dl_limit', 'application_status', 'is_reapplied_flg', 'upload_method', 'created_at_invalid')
    list_display_links = ('id', 'title',)

    def _file(self, row):
        return ','.join([x.name for x in row.file.all()])

    def _dest_user(self, row):
        return ','.join([x.full_name_preview for x in row.dest_user.all()])
    

class UrlUploadManageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', '_file', '_dest_user', 'application_status', 'is_reapplied_flg', 'upload_method', 'created_at_invalid')
    list_display_links = ('id', 'title',)

    def _file(self, row):
        return ','.join([x.name for x in row.file.all()])

    def _dest_user(self, row):
        return ','.join([x.full_name_preview for x in row.dest_user.all()])


class DownloadtableAdmin(admin.ModelAdmin):
    list_display = ('upload_manage', 'is_downloaded', 'dest_user', 'dowloaded_date', 'del_flag',)
    list_display_links = ('upload_manage', 'is_downloaded', 'dest_user', 'dowloaded_date', 'del_flag',)


class DownloadFiletableAdmin(admin.ModelAdmin):
    list_display = ('download_table', 'download_file', 'is_downloaded', 'dowloaded_date', 'del_flag',)
    list_display_links = ('download_table', 'download_file', 'is_downloaded', 'dowloaded_date', 'del_flag',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'last_name','first_name', 'email',)
    list_display_links = ('company_name', 'last_name','first_name', 'email',)


class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ('id', 'reg_user', 'reg_user_company', 'registration_date', 'is_approval_workflow', 'approval_format')
    list_display_links = ('id', 'reg_user', 'reg_user_company', 'registration_date', 'is_approval_workflow', 'approval_format',)


class FirstApproverRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_id','first_approver')
    list_display_links = ('id', 'company_id','first_approver',)


class SecondApproverRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_id','second_approver')
    list_display_links = ('id', 'company_id','second_approver',)


class ApprovalOperationLogAdmin(admin.ModelAdmin):
    list_display = ('operation_user', 'operation_user_company_id', 'operation_date','operation_content')
    list_display_links = ('operation_user', 'operation_user_company_id', 'operation_date','operation_content',)


class ApprovalManageAdmin(admin.ModelAdmin):
    list_display = ('id', 'manage_id', 'upload_manage', 'url_upload_manage', 'otp_upload_manage', 'guest_upload_manage', 'application_title', 'application_user','application_date', 'application_user_company_id', 'approval_status',
                    'approval_date', 'returned_date', 'first_approver', 'second_approver', 'is_rogical_deleted', 'is_reapplication_flg', 'upload_method')
    list_display_links = ('id', 'manage_id', 'upload_manage', 'url_upload_manage', 'otp_upload_manage', 'guest_upload_manage', 'application_title', 'application_user','application_date', 'application_user_company_id',
                            'approval_status', 'approval_date', 'returned_date', 'first_approver', 'second_approver', 'is_rogical_deleted', 'is_reapplication_flg',
                            'upload_method')


class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('upload_manage', 'url_upload_manage', 'otp_upload_manage', 'guest_upload_manage', 'approval_operation_user', 'approval_operation_user_position',
                    'approval_operation_user_company_id','approval_operation_date', 'approval_operation_content', 'message', 'manage_id')
    list_display_links = ('upload_manage', 'url_upload_manage', 'otp_upload_manage', 'guest_upload_manage', 'approval_operation_user',
                            'approval_operation_user_position', 'approval_operation_user_company_id','approval_operation_date',
                            'approval_operation_content', 'message')
    

class UserCustomGroupRelationAdmin(admin.ModelAdmin):
    list_display = ('group_id','group_user', 'approval_order')
    list_display_links = ('group_id','group_user', 'approval_order')


class CustomGroupRelationAdmin(admin.ModelAdmin):
    list_display = ('id','group_name', 'reg_user', 'reg_date')
    list_display_links = ('id','group_name', 'reg_user', 'reg_date')



class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('id','release_date', 'title','category','target_user','start_date','contents','maintenance_start_date','maintenance_end_date','maintenance_contents','maintenance_targets','maintenance_affects','maintenance_cancel_reason')#表示したいやつ
    list_display_links = ('id','release_date', 'title','category','target_user','start_date','contents','maintenance_start_date','maintenance_end_date','maintenance_contents','maintenance_targets','maintenance_affects','maintenance_cancel_reason')#クリックして変更したい時に


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','operation_user', 'operation',)#表示したいやつ
    list_display_links = ('id',)#クリックして変更したい時に


class OTPUploadManageAdmin(admin.ModelAdmin):
    list_display = ('id','title', '_file', '_dest_user',  'dest_user_mail1', 'dest_user_mail2', 'dest_user_mail3', 'dest_user_mail4', 'dest_user_mail5', 'dest_user_mail6', 'dest_user_mail7', 'dest_user_mail8',
                    '_dest_user_group', 'created_user', 'company', 'created_date', 'end_date', 'tmp_flag', 'is_downloaded', 'dl_limit', 'password',
                    'password_create_time', 'decode_token', 'url', 'file_del_flag', 'message', 'upload_method', 'created_at_invalid')
    list_display_links = ('id',)

    def _file(self, row):
        return ','.join([x.name for x in row.file.all()])

    def _dest_user(self, row):
        return ','.join([x.full_name_preview for x in row.dest_user.all()])

    def _dest_user_group(self, row):
        return ','.join([x.full_name_preview for x in row.dest_user_group.all()])


class OTPDownloadtableAdmin(admin.ModelAdmin):
    list_display = ('id','otp_upload_manage', 'is_downloaded', 'dest_user', 'dowloaded_date',
                    'del_flag', 'trash_flag')
    list_display_links = ('id',)


class OTPDownloadFiletableAdmin(admin.ModelAdmin):
    list_display = ('id','otp_download_table', 'download_file', 'is_downloaded', 'dowloaded_date',
                    'del_flag', 'otp_dl_count')
    list_display_links = ('id',)


class GuestUploadManageAdmin(admin.ModelAdmin):
    list_display = ('id','title', '_file', 'dest_user',  'dest_user_mail1', 'dest_user_mail2', 'dest_user_mail3', 'dest_user_mail4', 'dest_user_mail5', 'dest_user_mail6', 'dest_user_mail7', 'dest_user_mail8',
                    '_dest_user_group', 'created_user', 'company', 'created_date', 'end_date', 'tmp_flag', 'is_downloaded', 'password',
                    'password_create_time', 'decode_token', 'url', 'file_del_flag', 'message', 'url_invalid_flag', 'uploaded_date', 'upload_method', 'created_date', 'created_at_invalid')
    list_display_links = ('id',)

    def _file(self, row):
        return ','.join([x.name for x in row.file.all()])

    def _dest_user_group(self, row):
        return ','.join([x.full_name_preview for x in row.dest_user_group.all()])


class GuestUploadDownloadtableAdmin(admin.ModelAdmin):
    list_display = ('id','guest_upload_manage', 'is_downloaded', 'dest_user', 'dowloaded_date',
                    'del_flag', 'trash_flag')
    list_display_links = ('id',)


class GuestUploadDownloadFiletableAdmin(admin.ModelAdmin):
    list_display = ('id','guest_upload_download_table', 'download_file', 'is_downloaded', 'dowloaded_date',
                    'del_flag', 'guest_upload_dl_count')
    list_display_links = ('id',)


admin.site.register(Filemodel)
admin.site.register(UploadManage, UploadManageAdmin)
admin.site.register(PDFfilemodel)
admin.site.register(Downloadtable, DownloadtableAdmin)
admin.site.register(DownloadFiletable, DownloadFiletableAdmin)
admin.site.register(Group)
admin.site.register(UrlUploadManage, UrlUploadManageAdmin)
admin.site.register(UrlDownloadtable)
admin.site.register(UrlDownloadFiletable)
admin.site.register(Address)
admin.site.register(ApprovalWorkflow, ApprovalWorkflowAdmin)
admin.site.register(FirstApproverRelation, FirstApproverRelationAdmin)
admin.site.register(SecondApproverRelation, SecondApproverRelationAdmin)
admin.site.register(ApprovalOperationLog, ApprovalOperationLogAdmin)
admin.site.register(ApprovalManage, ApprovalManageAdmin)
admin.site.register(ApprovalLog, ApprovalLogAdmin)
admin.site.register(UserCustomGroupRelation, UserCustomGroupRelationAdmin)
admin.site.register(CustomGroup, CustomGroupRelationAdmin)
admin.site.register(OperationLog)
admin.site.register(Notification)

admin.site.register(OTPUploadManage, OTPUploadManageAdmin)
admin.site.register(OTPDownloadtable, OTPDownloadtableAdmin)
admin.site.register(OTPDownloadFiletable, OTPDownloadFiletableAdmin)

admin.site.register(GuestUploadManage, GuestUploadManageAdmin)
admin.site.register(GuestUploadDownloadtable, GuestUploadDownloadtableAdmin)
admin.site.register(GuestUploadDownloadFiletable, GuestUploadDownloadFiletableAdmin)