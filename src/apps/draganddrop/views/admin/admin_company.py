from django.shortcuts import render
from django.views.generic import TemplateView
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.views.home.home_common import CommonView
from accounts.models import User
import datetime
from django.db.models import Q
from django.conf import settings
import math

class ResourceManagementView(TemplateView,CommonView):
    template_name = 'draganddrop/ResourceManagement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 管理テーブル情報取得
        resource_management = ResourceManagement.objects.filter(company=self.request.user.company.id)
        context["resource_management"] = resource_management


        for resource_management in resource_management:
            date = datetime.datetime.now()
            resource_management.number_of_active_upload_manage = UploadManage.objects.filter(company = self.request.user.company.id, file_del_flag=0, end_date__gt=date).all().count()
            resource_management.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(company=self.request.user.company.id, file_del_flag=1) | Q(company = self.request.user.company.id, end_date__lt=date)).all().count() 
            resource_management.save()

            # 会社管理画面のレコード数とディスク使用量計算
            if resource_management:
                resource_management.total_record_size = (resource_management.number_of_active_upload_manage
                + resource_management.number_of_deactive_upload_manage
                + resource_management.number_of_active_url_upload_manage
                + resource_management.number_of_deactive_url_upload_manage
                + resource_management.number_of_download_table 
                + resource_management.number_of_download_file_table
                + resource_management.number_of_url_download_table
                + resource_management.number_of_url_download_file_table
                ) * settings.DEFAULT_RECORD_SIZE
                
                resource_management.total_size = (resource_management.total_record_size 
                + resource_management.total_file_size 
                )
                
                resource_management.save()

            # 登録ユーザー取得
            number_of_user = User.objects.filter(company=self.request.user.company.id).all().count()
            context["number_of_user"] = number_of_user

            # アップロード総件数
            total_upload_manage = resource_management.number_of_active_upload_manage + resource_management.number_of_deactive_upload_manage
            context["total_upload_manage"] = total_upload_manage if total_upload_manage < 9999 else ("9,999+")
            
            # URL共有総件数
            total_url_upload_manage = resource_management.number_of_active_url_upload_manage + resource_management.number_of_deactive_url_upload_manage
            context["total_url_upload_manage"] = total_url_upload_manage if total_url_upload_manage < 9999 else ("9,999+")

            units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")

            # ファイルサイズ合計取得
            total_file_size = resource_management.total_file_size

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
              
            # ディスク使用量取得
            total_size = resource_management.total_size
            
            i = math.floor(math.log(total_size, 1024)) if total_size > 0 else 0
            unit_size = round(total_size / 1024 ** i, 2)
            split = str(unit_size).split('.')
            number_of_digits = len(str(split[0]))
            if number_of_digits >= 3:
                i = math.ceil(math.log(total_size, 1024)) if total_size > 0 else 0
                unit_size = round(total_size / 1024 ** i, 2)
                context["total_size"] = unit_size
                context["total_size_unit"] = units[i]
            else:
                context["total_size"] = unit_size
                context["total_size_unit"] = units[i]

            # 使用量がMax1GBの場合(この値はプランによって変更予定)
            max_size = 1024 * 1024 * 1024
            percent = (total_size / max_size) * 100
            percent = round(percent) 
            context["total_percentage"] = percent

            # 残容量
            remaining_capacity = max_size - total_size
            i = math.floor(math.log(remaining_capacity, 1024)) if remaining_capacity > 0 else 0
            unit_size = round(remaining_capacity / 1024 ** i, 2)
            split = str(unit_size).split('.')
            remaining_capacity_number_of_digits = len(str(split[0]))
            if remaining_capacity_number_of_digits >= 3:
                i = math.ceil(math.log(remaining_capacity, 1024)) if remaining_capacity > 0 else 0
                unit_size = round(remaining_capacity / 1024 ** i, 2)
                context["remaining_capacity"] = unit_size
                context["remaining_capacity_unit"] = units[i]
            else:
                context["remaining_capacity"] = unit_size
                context["remaining_capacity_unit"] = units[i]

        return context


