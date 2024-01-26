from django.shortcuts import render
from django.views.generic import TemplateView
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, OTPUploadManage, GuestUploadManage, GuestUploadDownloadtable, ResourceManagement, PersonalResourceManagement
from draganddrop.views.home.home_common import CommonView
from accounts.models import User,Service,Company,FileupPermissions
from contracts.models import Plan, Contract, FileupDetail
import datetime
from django.db.models import Q
from django.conf import settings
import math

class ResourceManagementView(TemplateView,CommonView):
    template_name = 'draganddrop/ResourceManagement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        service = Service.objects.get(name="FileUP!")
        # 管理テーブル情報取得
        resource_management = ResourceManagement.objects.filter(company=self.request.user.company.id)
        context["resource_management"] = resource_management

        # ex_service = Service.objects.all()
        # context["ex_service"] = ex_service
        resource_contract = Contract.objects.get(company=user.company, service=service, status="2")
        context["resource_contract"] = resource_contract

        resource_detail = FileupDetail.objects.get(plan=resource_contract.plan)
        context["resource_detail"] = resource_detail
        # ログインしている会社情報取得

        for resource_management in resource_management:
            date = datetime.datetime.now()
            resource_management.number_of_active_upload_manage = UploadManage.objects.filter(company = self.request.user.company.id, file_del_flag=0, end_date__gt=date).all().count()
            resource_management.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(company=self.request.user.company.id, file_del_flag=1) | Q(company = self.request.user.company.id, end_date__lt=date)).all().count() 
            resource_management.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(company=self.request.user.company.id, file_del_flag=0, end_date__gt=date).all().count()
            resource_management.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(company=self.request.user.company.id, file_del_flag=1) | Q(company=self.request.user.company.id, end_date__lt=date)).all().count() 
            resource_management.number_of_active_otp_upload_manage = OTPUploadManage.objects.filter(company=self.request.user.company.id, file_del_flag=0, end_date__gt=date).all().count()
            resource_management.number_of_deactive_otp_upload_manage = OTPUploadManage.objects.filter(Q(company=self.request.user.company.id, file_del_flag=1) | Q(company=self.request.user.company.id, end_date__lt=date)).all().count() 
            resource_management.number_of_active_guest_upload_manage = GuestUploadManage.objects.filter(company=self.request.user.company.id, file_del_flag=0).all().count()
            resource_management.number_of_deactive_guest_upload_manage = GuestUploadManage.objects.filter(company=self.request.user.company.id, end_date__lt=date, uploaded_date__isnull=True).all().count() 
            resource_management.save()
            print('ここのなか',resource_management.number_of_removed_url_upload_manage)
            # 会社管理画面のレコード数とディスク使用量計算
            if resource_management:
                resource_management.total_record_size = (resource_management.number_of_active_upload_manage
                + resource_management.number_of_deactive_upload_manage
                + resource_management.number_of_active_url_upload_manage
                + resource_management.number_of_deactive_url_upload_manage
                + resource_management.number_of_active_otp_upload_manage
                + resource_management.number_of_deactive_otp_upload_manage
                + resource_management.number_of_active_guest_upload_manage
                + resource_management.number_of_deactive_guest_upload_manage
                + resource_management.number_of_download_table
                + resource_management.number_of_download_file_table
                + resource_management.number_of_url_download_table
                + resource_management.number_of_url_download_file_table
                + resource_management.number_of_otp_download_table
                + resource_management.number_of_otp_download_file_table
                + resource_management.number_of_guest_upload_download_table
                + resource_management.number_of_guest_upload_download_file_table
                ) * settings.DEFAULT_RECORD_SIZE #20KB(20480)

                resource_management.total_size = (resource_management.total_record_size
                + resource_management.total_file_size
                )

                resource_management.save()

            # 登録ユーザー取得
            permissions = FileupPermissions.objects.all()
            number_of_user = 0
            for permission in permissions:
                if permission.user.company == self.request.user.company:
                    number_of_user += 1
            context["number_of_user"] = number_of_user
            
            # 1レコードあたりの最大ファイルサイズ取得
            max_size_every_share = resource_detail.maxsize_every_share
            if max_size_every_share >= 1024:
                max_size_every_share_GB = max_size_every_share/1024
                context["max_size_every_share_GB"] = max_size_every_share_GB
            else:
                context["max_size_every_share"] = max_size_every_share
            

            # アップロード総件数
            total_upload_manage = resource_management.number_of_active_upload_manage + resource_management.number_of_deactive_upload_manage +  resource_management.number_of_removed_upload_manage
            context["total_upload_manage"] = total_upload_manage if total_upload_manage < 9999 else ("9,999+")
            
            # URL共有総件数
            total_url_upload_manage = resource_management.number_of_active_url_upload_manage + resource_management.number_of_deactive_url_upload_manage + resource_management.number_of_removed_url_upload_manage
            context["total_url_upload_manage"] = total_url_upload_manage if total_url_upload_manage < 9999 else ("9,999+")
            
            # OTP総件数
            total_otp_upload_manage = resource_management.number_of_active_otp_upload_manage + resource_management.number_of_deactive_otp_upload_manage + resource_management.number_of_removed_otp_upload_manage
            context["total_otp_upload_manage"] = total_otp_upload_manage if total_otp_upload_manage < 9999 else ("9,999+")

            # ゲストアップロード総件数
            total_guest_upload_manage = resource_management.number_of_active_guest_upload_manage + resource_management.number_of_deactive_guest_upload_manage + resource_management.number_of_removed_guest_upload_manage
            context["total_guest_upload_manage"] = total_guest_upload_manage if total_guest_upload_manage < 9999 else ("9,999+")

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
            print('トータルサイズとは',total_size)
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

            # 使用可能容量(この値はプランによって変更)
            max_size = (1024 * 1024 * 1024) * resource_detail.capacity
            # 1GB = 1024*1024*1024

            print('マックスサイズは----',max_size)
            percent = (total_size / max_size) * 100
            print('ぱーせんとはいくら1',percent)
            percent = round(percent) 
            print('ぱーせんとはいくら',percent)
            context["total_percentage"] = percent

            # 残容量
            remaining_capacity = max_size - total_size
            print('remaining_capacityとはーーー',remaining_capacity)
            i = math.floor(math.log(remaining_capacity, 1024)) if remaining_capacity > 0 else 0

            unit_size = round(remaining_capacity / 1024 ** i, 2)
            print('unit_sizeとはーーー',unit_size)

            split = str(unit_size).split('.')
            remaining_capacity_number_of_digits = len(str(split[0]))
            if remaining_capacity_number_of_digits >= 3:
                print('いふうえにきた')
                i = math.ceil(math.log(remaining_capacity, 1024)) if remaining_capacity > 0 else 0
                unit_size = round(remaining_capacity / 1024 ** i, 2)
                print('いふのなかのユニっとサイズ',unit_size)
                context["remaining_capacity"] = unit_size
                context["remaining_capacity_unit"] = units[i]
            else:
                print('いふしたにきた')
                context["remaining_capacity"] = unit_size
                context["remaining_capacity_unit"] = units[i]

        return context