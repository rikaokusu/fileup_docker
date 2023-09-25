from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import ContextMixin
from ...forms import ManageTasksStep1Form
from draganddrop.models import UploadManage, Downloadtable, UrlUploadManage, UrlDownloadtable, ResourceManagement, PersonalResourceManagement
from accounts.models import User
from django.urls import reverse
from django.urls import reverse
import datetime
from django.db.models import Q
from django.conf import settings
import math

# Token_LENGTH = 5  # ランダムURLを作成するためのTOKEN

class CommonView(ContextMixin):

    # ログインユーザーを返す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = User.objects.filter(pk=self.request.user.id).select_related().get()
        context["current_user"] = current_user

        url_name = self.request.resolver_match.url_name
        app_name = self.request.resolver_match.app_name

        context["url_name"] = url_name
        context["app_name"] = app_name
        context["current_user"] = current_user

        # 契約プラン
        plan = "light"
        context["plan"] = plan
        
        # 会社毎のファイル合計サイズ
        if ResourceManagement.objects.exists():
            resource_manage = ResourceManagement.objects.filter(company = self.request.user.company.id).first()
            if resource_manage:
                context["total_file_size"] = resource_manage.total_file_size
                # context["total_data_usage"] = resource_manage.total_data_usage
        
        return context


class FileuploadListView(LoginRequiredMixin, ListView, CommonView):
    model = UploadManage
    template_name = 'draganddrop/fileup_home.html'
    form_class = ManageTasksStep1Form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """送信テーブル"""
        # アップロード用
        user=self.request.user.id
        upload_manages = UploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["upload_manages"] = upload_manages

       # URLアップロード用
        url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["url_upload_manages"] = url_upload_manages

        """受信テーブル"""
        # ダウンロード用
        upload_manage_for_dest_users = Downloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0)
        context["upload_manage_for_dest_users"] = upload_manage_for_dest_users

        # URLダウンロード用
        url_upload_manage_for_dest_users = UrlDownloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0)
        context["url_upload_manage_for_dest_users"] = url_upload_manage_for_dest_users

        """ゴミ箱表示"""
        # アップロード用
        upload_manage_for_dest_users_deleted = Downloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=1)
        context["upload_manage_for_dest_users_deleted"] = upload_manage_for_dest_users_deleted

        # URLアップロード用
        url_upload_manage_for_dest_users_deleted = UrlDownloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=1)
        context["url_upload_manage_for_dest_users_deleted"] = url_upload_manage_for_dest_users_deleted

        """会社毎のレコード数取得"""
        number_of_company_upload_manage = UploadManage.objects.filter(company=self.request.user.company.id, tmp_flag=0).all().count()
        context["number_of_company_upload_manage"] = number_of_company_upload_manage

        # セッションに「_(アンダースコア)以外のセッション情報があった場合削除
        for key in list(self.request.session.keys()):
            if not key.startswith("_"):
                del self.request.session[key]

        return context


###########################
# 関数 個人管理画面計算処理  #
###########################
def total_data_usage(object, company, user, download_table, download_file_table, file_size, type):
    # 通常アップロード
    if type == 1:
        personal_resource_manage, created = PersonalResourceManagement.objects.get_or_create(user = user)
        if created:
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_upload_manage = 1
            personal_resource_manage.number_of_download_table =  download_table
            personal_resource_manage.number_of_download_file_table = download_file_table
            personal_resource_manage.upload_manage_file_size = file_size
            personal_resource_manage.save()
        else:
            date = datetime.datetime.now()
            
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_upload_manage = UploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_download_table = download_table
            personal_resource_manage.number_of_download_file_table = download_file_table
            personal_resource_manage.upload_manage_file_size = file_size
            personal_resource_manage.save()
    
    # URL共有
    else:
        personal_resource_manage, created = PersonalResourceManagement.objects.get_or_create(user = user)
        if created:
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_url_upload_manage = 1
            personal_resource_manage.number_of_url_download_table =  download_table
            personal_resource_manage.number_of_url_download_file_table = download_file_table
            personal_resource_manage.url_upload_manage_file_size = file_size
            personal_resource_manage.save()
        else:
            date = datetime.datetime.now()
            
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_url_download_table = download_table
            personal_resource_manage.number_of_url_download_file_table = download_file_table
            personal_resource_manage.url_upload_manage_file_size = file_size
            personal_resource_manage.save()
    
    # ファイルサイズ合計
    personal_resource_manage.total_file_size = personal_resource_manage.upload_manage_file_size + personal_resource_manage.url_upload_manage_file_size
    personal_resource_manage.save()

    # レコード総件数
    personal_resource_manage.total_record_size = (personal_resource_manage.number_of_active_upload_manage 
    + personal_resource_manage.number_of_deactive_upload_manage 
    + personal_resource_manage.number_of_active_url_upload_manage 
    + personal_resource_manage.number_of_deactive_url_upload_manage 
    + personal_resource_manage.number_of_download_table 
    + personal_resource_manage.number_of_download_file_table
    + personal_resource_manage.number_of_url_download_table
    + personal_resource_manage.number_of_url_download_file_table ) * settings.DEFAULT_RECORD_SIZE

    # データ使用量
    personal_resource_manage.total_data_usage = personal_resource_manage.total_record_size + personal_resource_manage.total_file_size

    personal_resource_manage.save()

    return personal_resource_manage

###############################
# 関数 個人管理画面送信テーブル削除処理  #
###############################
def send_table_delete(user, download_table, download_file_table, file_size, type):
    date = datetime.datetime.now()
    personal_resource_manages = PersonalResourceManagement.objects.filter(user = user)
    for personal_resource_manage in personal_resource_manages:
        if type == 1:
            personal_resource_manage.number_of_active_upload_manage = UploadManage.objects.filter(created_user=user, file_del_flag=0, tmp_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(created_user=user, file_del_flag=1, tmp_flag=0) | Q(created_user=user, end_date__lt=date, tmp_flag=0)).all().count() 
            personal_resource_manage.number_of_download_table -= download_table
            personal_resource_manage.number_of_download_file_table -= download_file_table
            personal_resource_manage.upload_manage_file_size -= file_size
            personal_resource_manage.save()
        else:
            personal_resource_manage.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_url_download_table -= download_table
            personal_resource_manage.number_of_url_download_file_table -= download_file_table
            personal_resource_manage.url_upload_manage_file_size -= file_size
            personal_resource_manage.save()

    # ファイルサイズ合計
    personal_resource_manage.total_file_size = personal_resource_manage.upload_manage_file_size + personal_resource_manage.url_upload_manage_file_size
    personal_resource_manage.save()

    # レコード総件数
    print("動いてる？？？？")
    print("-----", personal_resource_manage.number_of_url_download_file_table)
    personal_resource_manage.total_record_size = (personal_resource_manage.number_of_active_upload_manage 
    + personal_resource_manage.number_of_deactive_upload_manage 
    + personal_resource_manage.number_of_active_url_upload_manage 
    + personal_resource_manage.number_of_deactive_url_upload_manage 
    + personal_resource_manage.number_of_download_table 
    + personal_resource_manage.number_of_download_file_table
    + personal_resource_manage.number_of_url_download_table
    + personal_resource_manage.number_of_url_download_file_table ) * settings.DEFAULT_RECORD_SIZE
    # データ使用量
    personal_resource_manage.total_data_usage = personal_resource_manage.total_record_size + personal_resource_manage.total_file_size

    personal_resource_manage.save()

    return send_table_delete

###############################
# 関数 会社管理画面計算処理  #
###############################
def resource_management_calculation_process(company):

    # 個人管理データから同じ会社のオブジェクトを取得する
    personal_resource_manages = PersonalResourceManagement.objects.filter(company = company)

    # 会社管理データ作成・更新
    resource_manage, created = ResourceManagement.objects.get_or_create(company = company)
    download_table = 0
    url_download_table = 0
    download_file_table = 0
    url_download_file_table = 0
    total_file_size = 0
    number_of_active_upload_manage = 0
    number_of_deactive_upload_manage = 0
    number_of_active_url_upload_manage = 0
    number_of_deactive_url_upload_manage = 0
    for personal_resource_manage in personal_resource_manages:
        download_table += personal_resource_manage.number_of_download_table
        url_download_table += personal_resource_manage.number_of_url_download_table
        download_file_table += personal_resource_manage.number_of_download_file_table
        url_download_file_table += personal_resource_manage.number_of_url_download_file_table
        total_file_size += personal_resource_manage.total_file_size
        number_of_active_upload_manage += personal_resource_manage.number_of_active_upload_manage
        number_of_deactive_upload_manage += personal_resource_manage.number_of_deactive_upload_manage
        number_of_active_url_upload_manage += personal_resource_manage.number_of_active_url_upload_manage
        number_of_deactive_url_upload_manage += personal_resource_manage.number_of_deactive_url_upload_manage
        date = datetime.datetime.now()

        if created:
            resource_manage.number_of_active_upload_manage = number_of_active_upload_manage
            resource_manage.number_of_deactive_upload_manage = number_of_deactive_upload_manage
            resource_manage.number_of_active_url_upload_manage = number_of_active_url_upload_manage
            resource_manage.number_of_deactive_url_upload_manage = number_of_deactive_url_upload_manage
        else:
            resource_manage.number_of_active_upload_manage = UploadManage.objects.filter(company = company, file_del_flag=0, end_date__gt=date).all().count()
            resource_manage.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(company=company, file_del_flag=1) | Q(company = company, end_date__lt=date)).all().count() 
            resource_manage.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(company = company, file_del_flag=0, end_date__gt=date).all().count()
            resource_manage.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(company=company, file_del_flag=1) | Q(company = company, end_date__lt=date)).all().count() 

        resource_manage.number_of_download_table = download_table
        resource_manage.number_of_download_file_table = download_file_table
        resource_manage.number_of_url_download_table = url_download_table
        resource_manage.number_of_url_download_file_table = url_download_file_table
        resource_manage.total_file_size = total_file_size
        resource_manage.save()

    # レコード総件数
    resource_manage.total_record_size = (resource_manage.number_of_active_upload_manage 
    + resource_manage.number_of_deactive_upload_manage 
    + resource_manage.number_of_active_url_upload_manage 
    + resource_manage.number_of_deactive_url_upload_manage 
    + resource_manage.number_of_download_table 
    + resource_manage.number_of_download_file_table
    + resource_manage.number_of_url_download_table
    + resource_manage.number_of_url_download_file_table ) * settings.DEFAULT_RECORD_SIZE

    # データ使用量
    resource_manage.total_data_usage = resource_manage.total_record_size + resource_manage.total_file_size

    resource_manage.save()

    return resource_management_calculation_process






