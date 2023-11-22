from django.contrib import admin

from .models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, Address,OperationLog
# Register your models here.



class UploadManageAdmin(admin.ModelAdmin):
    list_display = ('title', '_file', '_dest_user', 'dest_user_mail1', 'dest_user_mail2', 'dest_user_mail3', 'dest_user_mail4', 'dest_user_mail5', 'dest_user_mail6', 'dest_user_mail7', 'dest_user_mail8', 'created_user', 'created_date', 'end_date', 'tmp_flag', 'file_del_flag', 'is_downloaded', 'dl_limit')
    list_display_links = ('title',)

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

class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('id','operation_user', 'operation',)#表示したいやつ
    list_display_links = ('id',)#クリックして変更したい時に

admin.site.register(Filemodel)
admin.site.register(UploadManage, UploadManageAdmin)
admin.site.register(PDFfilemodel)
admin.site.register(Downloadtable, DownloadtableAdmin)
admin.site.register(DownloadFiletable, DownloadFiletableAdmin)
admin.site.register(Group)
admin.site.register(UrlUploadManage)
admin.site.register(UrlDownloadtable)
admin.site.register(UrlDownloadFiletable)
admin.site.register(Address)
admin.site.register(OperationLog)
