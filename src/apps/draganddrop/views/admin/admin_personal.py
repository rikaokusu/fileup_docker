from django.shortcuts import render
from django.views.generic import TemplateView
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from accounts.models import User
from draganddrop.views.home.home_common import CommonView
import datetime
from django.db.models import Q
from django.conf import settings
import math

class PersonalResourceManagementView(TemplateView,CommonView):
    template_name = 'draganddrop/PersonalResourceManagement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 管理テーブル情報取得
        personal_resource_management = PersonalResourceManagement.objects.filter(user=self.request.user.id)
        context["personal_resource_management"] = personal_resource_management
        
        upload_manages = UploadManage.objects.filter(id=self.request.user.id).all()
        
        for personal_resource_management in personal_resource_management:

            # アップロード件数とURL共有件数の更新
            if personal_resource_management:
                date = datetime.datetime.now()
                personal_resource_management.number_of_active_upload_manage = UploadManage.objects.filter(created_user=self.request.user.id, file_del_flag=0, end_date__gt=date).all().count()
                personal_resource_management.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(created_user=self.request.user.id, file_del_flag=1) | Q(created_user=self.request.user.id, end_date__lt=date)).all().count() 
                personal_resource_management.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(created_user=self.request.user.id, file_del_flag=0, end_date__gt=date).all().count()
                personal_resource_management.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(created_user=self.request.user.id, file_del_flag=1) | Q(created_user=self.request.user.id, end_date__lt=date)).all().count() 
                
                # レコード総件数とデータ使用量計算
                personal_resource_management.total_record_size = (personal_resource_management.number_of_active_upload_manage 
                + personal_resource_management.number_of_deactive_upload_manage 
                + personal_resource_management.number_of_active_url_upload_manage 
                + personal_resource_management.number_of_deactive_url_upload_manage 
                + personal_resource_management.number_of_download_table 
                + personal_resource_management.number_of_download_file_table
                + personal_resource_management.number_of_url_download_table
                + personal_resource_management.number_of_url_download_file_table) * settings.DEFAULT_RECORD_SIZE
                
                personal_resource_management.total_data_usage = personal_resource_management.total_record_size + personal_resource_management.total_file_size
                personal_resource_management.save()

              
            # アップロード総件数
            total_upload_manage = personal_resource_management.number_of_active_upload_manage + personal_resource_management.number_of_deactive_upload_manage
            context["total_upload_manage"] = total_upload_manage if total_upload_manage < 9999 else ("9,999+")
            
            # URL共有総件数
            total_url_upload_manage = personal_resource_management.number_of_active_url_upload_manage + personal_resource_management.number_of_deactive_url_upload_manage + personal_resource_management.number_of_removed_url_upload_manage
            context["total_url_upload_manage"] = total_url_upload_manage if total_url_upload_manage < 9999 else ("9,999+")

            units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")

            # ファイルサイズ合計取得
            total_file_size = personal_resource_management.total_file_size

            i = math.floor(math.log(total_file_size, 1024)) if total_file_size > 0 else 0
            total_file_unit_size = round(total_file_size / 1024 ** i, 2)
            split = str(total_file_unit_size).split('.')
            file_size_number_of_digits = len(str(split[0]))
            if file_size_number_of_digits >= 3:
                i = math.ceil(math.log(total_file_size, 1024)) if total_file_size > 0 else 0
                total_file_unit_size = round(total_file_size / 1024 ** i, 2)
                context["total_file_size"] = total_file_unit_size
                context["unit"] = units[i]
            else:
                context["total_file_size"] = total_file_unit_size
                context["unit"] = units[i]
 
            # データ使用量取得
            total_data_usage = personal_resource_management.total_data_usage

            i = math.floor(math.log(total_data_usage, 1024)) if total_data_usage > 0 else 0
            unit_size = round(total_data_usage / 1024 ** i, 2)
            split = str(unit_size).split('.')
            number_of_digits = len(str(split[0]))
            if number_of_digits >= 3:
                i = math.ceil(math.log(total_data_usage, 1024)) if total_data_usage > 0 else 0
                unit_size = round(total_data_usage / 1024 ** i, 2)
                context["total_data_usage"] = unit_size
                context["total_data_usage_unit"] = units[i]
            else:
                context["total_data_usage"] = unit_size
                context["total_data_usage_unit"] = units[i]

        return context

