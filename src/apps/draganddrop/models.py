from django.db import models
from django.conf import settings
from accounts.models import User, Service, Company,FileupPermissions
from contracts.models import Contract, Plan
import uuid
from datetime import date
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_mysql.models import ListCharField
import os

# Create your models here.
Legal_Personality = (
    (0, 'なし'),
    (1, '株式会社'),
    (2, '合同会社'),
    (3, '合資会社'),
    (4, '合名会社'),
    )
class Address(models.Model):
    # ユーザー登録者
    created_user = models.CharField(max_length=245, blank=True, null=True)
    # 種別
    legal_or_individual = models.IntegerField(verbose_name='', default=0)
    # 法人格
    legal_personality = models.IntegerField(
        verbose_name='法人格', default=0, null=True, blank=True, choices=Legal_Personality)
    # 法人格前後
    legal_person_posi = models.IntegerField(
        verbose_name='', default=0, null=True, blank=True)
    # 法人名
    company_name = models.CharField('法人名', null=True, blank=True, max_length=255)
    # 屋号名
    trade_name = models.CharField('屋号名', null=True, blank=True, max_length=255)
    # 部署名
    department_name = models.CharField('部署名', null=True, blank=True, max_length=255)
    # 姓
    last_name = models.CharField('氏名', max_length=255, blank=True)
    # 名
    first_name = models.CharField('氏名', max_length=255, blank=True)
    # メールアドレス
    email = models.CharField('メールアドレス', max_length=255, blank=True)
    # メールアドレス直接入力
    is_direct_email = models.BooleanField(null=True, blank=True, default=False)
    # 表示名プレビュー
    full_name_preview = models.CharField('表示名プレビュー', max_length=255, blank=True)
    def __str__(self):
        name = self.full_name_preview
        return name

class Group(models.Model):
    # Group名
    group_name = models.CharField('グループ名', null=True, blank=True, max_length=255)
    # 表示名（法人名）
    address = models.ManyToManyField(Address, verbose_name=('address'), blank=True)
    # グループ作成者
    created_user = models.CharField(max_length=245, blank=True, null=True)

    def __str__(self):
        name = self.group_name
        return name

class Filemodel(models.Model):
    
    def upload_name(instance, filename):
        name=str(instance)
        print('ネームの中身',name)
        model_name = instance._meta.verbose_name.replace(' ', '-')
        print('モデルネームの中身',model_name)
        user = User.objects.filter(pk=instance.created_user).first()
        cont = Contract.objects.filter(company=user.company,service__name='FileUP!',status='2').first()
        if not cont.plan.name == 'フリープラン':
            return "charge" + "/"  + filename
        else:
            return "free" + "/"  + filename

    size = models.CharField(max_length=140)
    name = models.CharField(max_length=140)
    upload = models.FileField(upload_to=upload_name)
    del_flag = models.IntegerField(null=True, blank=True, default=0)
    created_user = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        name = self.name
        return name


APPLICATION_STATUS_CHOICE = (
    (1, '申請中'),
    (2, '一次承認待ち'),
    (3, '最終承認待ち'),
    (4, 'キャンセル'),
)

class UploadManage(models.Model):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=140)
    file = models.ManyToManyField(Filemodel, verbose_name=('file'), blank=True)
    dest_user = models.ManyToManyField(Address, blank=True)
    dest_user_mail1 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail2 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail3 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail4 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail5 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail6 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail7 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail8 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_group = models.ManyToManyField(Group, blank=True)
    company = models.CharField(max_length=245, blank=True, null=True) 
    created_user = models.CharField(max_length=245, blank=True, null=True)
    created_date = models.DateTimeField(verbose_name='開始日時', blank=True, null=True,)
    end_date = models.DateTimeField(verbose_name='終了日時', blank=False, null=True)
    tmp_flag = models.IntegerField(null=True, blank=True, default=0)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dl_limit = models.IntegerField(verbose_name='ダウンロード回数', default=0, blank=True)
    file_del_flag = models.IntegerField(null=True, blank=True, default=0)
    message = models.CharField(max_length=140, null=True, blank=True)
    # 申請ステータス
    application_status = models.IntegerField('申請ステータス', choices=APPLICATION_STATUS_CHOICE, default=1)

    @property
    def is_past_due(self):
        return date.today() > self.end_date

    def __str__(self):
        title = self.title
        return title


class PDFfilemodel(models.Model):
    file = models.OneToOneField(Filemodel, verbose_name='file', on_delete=models.CASCADE, null=True)
    size = models.CharField(max_length=140, null=True)
    name = models.CharField(max_length=140, null=True)
    upload = models.FileField(upload_to='file', null=True)

# ユーザー毎のダウンロード状況を管理するためのテーブル
class Downloadtable(models.Model):
    upload_manage = models.ForeignKey(UploadManage, on_delete=models.CASCADE, related_name='uploadmanage', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dest_user = models.ForeignKey(Address, related_name='downloadtable_dest_user', on_delete=models.CASCADE, blank=True, null=True)
    dowloaded_date = models.DateTimeField(verbose_name='ダウンロード日時', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    trash_flag = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        full_name_preview = self.dest_user.full_name_preview
        return full_name_preview


# ファイル毎のダウンロード状況を管理するためのテーブル
class DownloadFiletable(models.Model):
    download_table = models.ForeignKey(Downloadtable, on_delete=models.CASCADE, related_name='downloadtable', null=True)
    download_file = models.ForeignKey(Filemodel, on_delete=models.CASCADE, related_name='download_file', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dowloaded_date = models.DateTimeField(verbose_name='ダウンロード日時', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    dl_count = models.IntegerField(default=0)


# class logtable(models.Model):
#     user = models.CharField(max_length=245, blank=True, null=True)
#     date = models.DateTimeField(default=timezone.now)
#     file = models.ManyToManyField(Filemodel, verbose_name=('file'), blank=True)
#     text = models.CharField(max_length=140)


class UrlUploadManage(models.Model):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=140)
    file = models.ManyToManyField(Filemodel, verbose_name=('file'), blank=True)
    dest_user = models.ManyToManyField(Address, blank=True)
    dest_user_mail1 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail2 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail3 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail4 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail5 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail6 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail7 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail8 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_group = models.ManyToManyField(Group, blank=True)
    created_user = models.CharField(max_length=245, blank=True, null=True)
    company = models.CharField(max_length=245, blank=True, null=True) 
    created_date = models.DateTimeField(verbose_name='作成日時', blank=True, null=True,)
    end_date = models.DateTimeField(verbose_name='終了日時', blank=False, null=True)
    tmp_flag = models.IntegerField(null=True, blank=True, default=0)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    auth_meth = models.IntegerField(verbose_name='認証方法', default=0, blank=True)
    dl_limit = models.IntegerField(verbose_name='ダウンロード回数', default=0, blank=True)
    password = models.CharField(max_length=140, null=True, blank=True)
    decode_token = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=140, null=True, blank=True)
    file_del_flag = models.IntegerField(null=True, blank=True, default=0)
    message = models.CharField(max_length=140, blank=True, null=True)

    @property
    def is_past_due(self):
        return date.today() > self.end_date

    def __str__(self):
        title = self.title
        return title


class UrlDownloadtable(models.Model):
    url_upload_manage = models.ForeignKey(UrlUploadManage, on_delete=models.CASCADE, related_name='url_uploadmanage', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dest_user = models.ForeignKey(Address, related_name='url_downloadtable_dest_user', on_delete=models.CASCADE, blank=True, null=True)
    dowloaded_date = models.DateTimeField(verbose_name='サンプル項目4 期間 開始日', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    trash_flag = models.IntegerField(null=True, blank=True, default=0)


class UrlDownloadFiletable(models.Model):
    url_download_table = models.ForeignKey(UrlDownloadtable, on_delete=models.CASCADE, related_name='url_download_table', null=True)
    download_file = models.ForeignKey(Filemodel, on_delete=models.CASCADE, related_name='url_download_file', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dowloaded_date = models.DateTimeField(verbose_name='サンプル項目4 期間 開始日', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    url_dl_count = models.IntegerField(default=0)

## OTPテーブル ##
class OTPUploadManage(models.Model):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=140)
    file = models.ManyToManyField(Filemodel, verbose_name=('file'), blank=True)
    dest_user = models.ManyToManyField(Address, blank=True)
    dest_user_mail1 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail2 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail3 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail4 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail5 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail6 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail7 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail8 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_group = models.ManyToManyField(Group, blank=True)
    created_user = models.CharField(max_length=245, blank=True, null=True)
    company = models.CharField(max_length=245, blank=True, null=True) 
    created_date = models.DateTimeField(verbose_name='作成日時', blank=True, null=True,)
    end_date = models.DateTimeField(verbose_name='終了日時', blank=False, null=True)
    tmp_flag = models.IntegerField(null=True, blank=True, default=0)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dl_limit = models.IntegerField(verbose_name='ダウンロード回数', default=0, blank=True)
    password = models.CharField(max_length=10, null=True, blank=True)
    password_create_time = models.DateTimeField(verbose_name='OTP作成日時', blank=True, null=True,)
    decode_token = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=140, null=True, blank=True)
    file_del_flag = models.IntegerField(null=True, blank=True, default=0)
    message = models.CharField(max_length=140, blank=True, null=True)

    @property
    def is_past_due(self):
        return date.today() > self.end_date

    def __str__(self):
        title = self.title
        return title


class OTPDownloadtable(models.Model):
    otp_upload_manage = models.ForeignKey(OTPUploadManage, on_delete=models.CASCADE, related_name='otp_uploadmanage', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dest_user = models.ForeignKey(Address, related_name='otp_downloadtable_dest_user', on_delete=models.CASCADE, blank=True, null=True)
    dowloaded_date = models.DateTimeField(verbose_name='サンプル項目4 期間 開始日', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    trash_flag = models.IntegerField(null=True, blank=True, default=0)


class OTPDownloadFiletable(models.Model):
    otp_download_table = models.ForeignKey(OTPDownloadtable, on_delete=models.CASCADE, related_name='otp_download_table', null=True)
    download_file = models.ForeignKey(Filemodel, on_delete=models.CASCADE, related_name='otp_download_file', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dowloaded_date = models.DateTimeField(verbose_name='サンプル項目4 期間 開始日', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    otp_dl_count = models.IntegerField(default=0)


## ゲストアップロードテーブル ##
class GuestUploadManage(models.Model):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=140)
    file = models.ManyToManyField(Filemodel, verbose_name=('file'), blank=True)
    dest_user = models.ManyToManyField(Address, blank=True)
    dest_user_mail1 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail2 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail3 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail4 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail5 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail6 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail7 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_mail8 = models.EmailField(max_length=100, null=True, blank=True)
    dest_user_group = models.ManyToManyField(Group, blank=True)
    guest_user_mail = models.EmailField(verbose_name='ゲストユーザーメールアドレス',max_length=100, null=True, blank=True)
    guest_user_name = models.CharField(verbose_name='ゲストユーザー名',max_length=245, blank=True, null=True)
    created_user = models.CharField(max_length=245, blank=True, null=True)
    company = models.CharField(max_length=245, blank=True, null=True) 
    created_date = models.DateTimeField(verbose_name='作成日時', blank=True, null=True,)
    end_date = models.DateTimeField(verbose_name='リクエスト終了日時', blank=False, null=True)
    tmp_flag = models.IntegerField(null=True, blank=True, default=0)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    password = models.CharField(max_length=10, null=True, blank=True)
    password_create_time = models.DateTimeField(verbose_name='OTP作成日時', blank=True, null=True,)
    decode_token = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=140, null=True, blank=True)
    file_del_flag = models.IntegerField(null=True, blank=True, default=0)
    message = models.CharField(max_length=140, blank=True, null=True)
    url_invalid_flag = models.IntegerField(verbose_name='ゲストへのURL招待無効フラグ',null=True, blank=True, default=0)

    @property
    def is_past_due(self):
        return date.today() > self.end_date

    def __str__(self):
        title = self.title
        return title

class GuestUploadDownloadtable(models.Model):
    guest_upload_manage = models.ForeignKey(GuestUploadManage, on_delete=models.CASCADE, related_name='guest_uploadmanage', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dest_user = models.ForeignKey(Address, related_name='guest_downloadtable_dest_user', on_delete=models.CASCADE, blank=True, null=True)
    dowloaded_date = models.DateTimeField(verbose_name='ダウンロード日', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    trash_flag = models.IntegerField(null=True, blank=True, default=0)

class GuestUploadDownloadFiletable(models.Model):
    guest_upload_download_table = models.ForeignKey(GuestUploadDownloadtable, on_delete=models.CASCADE, related_name='guest_upload_download_table', null=True)
    download_file = models.ForeignKey(Filemodel, on_delete=models.CASCADE, related_name='guest_upload_download_file', null=True)
    is_downloaded = models.BooleanField(null=True, blank=True, default=False)
    dowloaded_date = models.DateTimeField(verbose_name='ダウンロード日', blank=True, null=True,)
    del_flag = models.BooleanField(null=True, blank=True, default=False)
    guest_upload_dl_count = models.IntegerField(default=0)


## 会社・個人管理テーブル ##
class PersonalResourceManagement(models.Model):
    company = models.CharField(max_length=245, blank=True, null=True) 
    user = models.CharField(max_length=245, blank=True, null=True)
    number_of_active_upload_manage = models.IntegerField(blank=True, null=True, default=0) #アップロード有効送信レコード
    number_of_deactive_upload_manage = models.IntegerField(blank=True, null=True, default=0) #アップロード無効送信レコード
    number_of_active_url_upload_manage = models.IntegerField(blank=True, null=True, default=0) #URL共有有効レコード
    number_of_deactive_url_upload_manage = models.IntegerField(blank=True, null=True, default=0) #URL共有無効レコード
    number_of_active_otp_upload_manage = models.IntegerField(blank=True, null=True, default=0) #OTP有効レコード
    number_of_deactive_otp_upload_manage = models.IntegerField(blank=True, null=True, default=0) #OTP無効レコード
    number_of_active_guest_upload_manage = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロード有効レコード
    number_of_deactive_guest_upload_manage = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロード無効レコード
    number_of_download_table = models.IntegerField(blank=True, null=True, default=0) #ユーザー毎DL状況確認レコード
    number_of_url_download_table = models.IntegerField(blank=True, null=True, default=0) #URL共有ユーザー毎DL状況確認レコード
    number_of_otp_download_table = models.IntegerField(blank=True, null=True, default=0) #OTPユーザー毎DL状況確認レコード
    number_of_guest_upload_download_table = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロードユーザー毎DL状況確認レコード
    number_of_download_file_table = models.IntegerField(blank=True, null=True, default=0) #ファイル毎DL状況確認レコード
    number_of_url_download_file_table = models.IntegerField(blank=True, null=True, default=0) #URL共有ファイル毎DL状況確認レコード
    number_of_otp_download_file_table = models.IntegerField(blank=True, null=True, default=0) #OTPファイル毎DL状況確認レコード
    number_of_guest_upload_download_file_table = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロードファイル毎DL状況確認レコード
    number_of_removed_upload_manage = models.IntegerField(blank=True, null=True, default=0) #アップロード削除済みレコード数
    number_of_removed_url_upload_manage = models.IntegerField(blank=True, null=True, default=0) #URL共有削除済みレコード数
    number_of_removed_otp_upload_manage = models.IntegerField(blank=True, null=True, default=0) #OTP削除済みレコード数
    number_of_removed_guest_upload_manage = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロード削除済みレコード数
    total_record_size = models.IntegerField(blank=True, null=True, default=0)
    upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    url_upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    otp_upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    guest_upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    total_file_size = models.IntegerField(blank=True, null=True, default=0)
    total_data_usage = models.IntegerField(blank=True, null=True, default=0)

class ResourceManagement(models.Model):
    company = models.CharField(max_length=245, blank=True, null=True) 
    number_of_active_upload_manage = models.IntegerField(blank=True, null=True, default=0)
    number_of_deactive_upload_manage = models.IntegerField(blank=True, null=True, default=0)
    number_of_active_url_upload_manage = models.IntegerField(blank=True, null=True, default=0)
    number_of_deactive_url_upload_manage = models.IntegerField(blank=True, null=True, default=0)
    number_of_active_otp_upload_manage = models.IntegerField(blank=True, null=True, default=0) #OTP有効レコード
    number_of_deactive_otp_upload_manage = models.IntegerField(blank=True, null=True, default=0) #OTP無効レコード
    number_of_active_guest_upload_manage = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロード有効レコード
    number_of_deactive_guest_upload_manage = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロード無効レコード
    number_of_download_table = models.IntegerField(blank=True, null=True, default=0)
    number_of_url_download_table = models.IntegerField(blank=True, null=True, default=0)
    number_of_otp_download_table = models.IntegerField(blank=True, null=True, default=0) #OTPユーザー毎DL状況確認レコード
    number_of_guest_upload_download_table = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロードユーザー毎DL状況確認レコード
    number_of_download_file_table = models.IntegerField(blank=True, null=True, default=0)
    number_of_url_download_file_table = models.IntegerField(blank=True, null=True, default=0)
    number_of_otp_download_file_table = models.IntegerField(blank=True, null=True, default=0) #OTPファイル毎DL状況確認レコード
    number_of_guest_upload_download_file_table = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロードファイル毎DL状況確認レコード
    number_of_removed_upload_manage = models.IntegerField(blank=True, null=True, default=0) #アップロード削除済みレコード数
    number_of_removed_url_upload_manage = models.IntegerField(blank=True, null=True, default=0) #URL共有削除済みレコード数
    number_of_removed_otp_upload_manage = models.IntegerField(blank=True, null=True, default=0) #OTP削除済みレコード数
    number_of_removed_guest_upload_manage = models.IntegerField(blank=True, null=True, default=0) #ゲストアップロード削除済みレコード数
    total_record_size = models.IntegerField(blank=True, null=True, default=0) 
    upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    url_upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    otp_upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    guest_upload_manage_file_size = models.IntegerField(blank=True, null=True, default=0)
    total_file_size = models.IntegerField(blank=True, null=True, default=0)
    total_data_usage = models.IntegerField(blank=True, null=True, default=0)

class Plan(models.Model):
    plan_id = models.CharField('プランID', max_length=32, blank=False, default="plan")
    name = models.CharField('プラン名', max_length=30, blank=False)
    user_limit = models.IntegerField('ユーザー数上限', blank=True, default=0)
    usable_capacity = models.IntegerField('使用可能容量', blank=True, default=0)
    sharing_url = models.BooleanField('URL共有可否',default=False, blank=True)
    download_expiration = models.IntegerField('ダウンロード期限', blank=True, null=True)


"""
承認ワークフロー 基本設定
"""

IS_APPROVA_WORKFLOW = (
    (1, '使用する'),
    (2, '使用しない'),
)

APPROVAL_FORMAT = (
    (1, '１人が承認すれば次の承認者に進む'),
    (2, '全員が承認すると次の承認者に進む'),
)

class ApprovalWorkflow(models.Model):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 登録ユーザー
    reg_user = models.CharField('登録ユーザー', max_length=255, blank=True, null=True)
    # 会社
    reg_user_company = models.CharField('会社', max_length=255, blank=True, null=True)
    # 登録日
    registration_date = models.DateTimeField('登録日', default=timezone.now)
    # 承認ワークフロー
    is_approval_workflow = models.IntegerField(
        verbose_name='承認ワークフロー', default=0, null=True, blank=True, choices=IS_APPROVA_WORKFLOW)
    # 承認形式
    approval_format = models.IntegerField(
        verbose_name='承認形式', default=0, null=True, blank=True, choices=APPROVAL_FORMAT)


"""
一次承認者(自作中間テーブル)
"""
class FirstApproverRelation(models.Model):
    # 会社のID
    company_id = models.CharField(max_length=500, verbose_name="会社のID", null=True, blank=True)

    # 一次承認者
    first_approver = models.CharField(max_length=500, verbose_name="一次承認者", null=True, blank=True)


"""
二次承認者(自作中間テーブル)
"""
class SecondApproverRelation(models.Model):
    # 会社のID
    company_id = models.CharField(max_length=500, verbose_name="会社のID", null=True, blank=True)

    # 二次承認者
    second_approver = models.CharField(max_length=500, verbose_name="二次承認者", null=True, blank=True)


OPERATION_CONTENT = (
    (1, '承認ワークフロー変更'),
    (2, '承認形式変更'),
    (3, '一次承認者変更'),
    (4, '二次承認者変更'),
)

"""
操作履歴
"""
class ApprovalOperationLog(models.Model):
    # 操作ユーザー
    operation_user = models.CharField('操作ユーザー', max_length=255, blank=True, null=True)
    # 操作ユーザーの会社のID
    operation_user_company_id = models.CharField(max_length=500, verbose_name="操作ユーザーの会社のID", null=True, blank=True)
    # 操作日時
    operation_date = models.DateTimeField('操作日時', default=timezone.now)
    # 操作
    operation_content = models.IntegerField(
        verbose_name='操作', default=0, null=True, blank=True, choices=OPERATION_CONTENT)


"""
承認申請
"""

APPLOVAL_STATUS_CHOICE = (
    (1, '未承認'),
    (2, '承認済み'),
    (3, '差戻し'),
)

class ApprovalManage(models.Model):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ファイルアップロード
    upload_mange = models.ForeignKey(UploadManage, on_delete=models.CASCADE, null=True, related_name='upload_mange')
    # 申請件名
    application_title = models.CharField('申請件名', max_length=500, blank=True, null=True)
    # 申請ユーザー
    application_user = models.CharField('申請ユーザー', max_length=255, blank=True, null=True)
    # 申請日時
    application_date = models.DateTimeField('申請日時', default=timezone.now)
    # 申請ユーザーの会社のID
    application_user_company_id = models.CharField('申請ユーザーの会社のID', max_length=500, null=True, blank=True)
    # 承認ステータス
    approval_status = models.IntegerField('承認ステータス', choices=APPLOVAL_STATUS_CHOICE, default=1)
    # 一次承認者
    first_approver = models.CharField('一次承認者', max_length=500, blank=True, null=True)
    # 二次承認者
    second_approver = models.CharField('二次承認者', max_length=500, blank=True, null=True)
    # 承認日時
    approval_date = models.DateTimeField('承認日時',  blank=True, null=True)


##############  操作ログ
class OperationLog(models.Model):
    OPERATION_LOG_CATEGORY = (
    (0, 'なし'),
    (1, 'ログイン'),
    (2, 'ファイル共有'),
    (3, 'アドレス帳'),
    (4, 'ユーザー権限'),
    (5, '組織設定'),
    )
    OPERATION_LOG_OPERATION = (
    (0, 'なし'),
    (1, '作成'),
    (2, '変更'),
    (3, '削除'),
    (4, '登録'),
    )
    UPLOAD_LOG_CATEGORY = (
    (0,'通常アップロード'),
    (1,'URL共有'),
    (2,'OTP共有'),
    (3,'一括'),
    (4,'ユーザー'),
    (5,'グループ'),
    )
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 操作日時
    created_date = models.DateTimeField(_('作成日時'), default=timezone.now, blank=True)
    # 操作した人
    operation_user = models.CharField(_('操作した人'), max_length=64, null=True) 
    # 操作したIPアドレス
    client_addr = models.CharField(_('IPアドレス'), max_length=64, null=True) #1
    # カテゴリ
    category = models.IntegerField(_('カテゴリ'), default='0', choices=OPERATION_LOG_CATEGORY)
    # 操作種別
    operation = models.IntegerField(_('オペレーション'), default='0', choices=OPERATION_LOG_OPERATION)
    # 宛先メールアドレス=通常、URL,OTPで参照するテーブルが別？
    destination_address=models.CharField(_('宛先メールアドレス'),max_length=999, null=True)
    # ファイルタイトル
    file_title = models.CharField(_(')ファイルタイトル'),max_length=64,null=True)
    # # 対象ファイル名
    # log_filename = models.ForeignKey(Filemodel, on_delete=models.CASCADE, related_name='log_filename', null=True)
    # # 対象ファイル名
    file_name = models.CharField(_(')ファイル名'),max_length=64,null=True)
    # 共有種別（通常、URL,OTP）
    upload_category = models.IntegerField(_('共有種別'), default='0', choices=UPLOAD_LOG_CATEGORY,null=True)

# # 操作ログ用のファイルテーブル
# class LogFile(models.Model):
#     # 操作ログ紐づけ
#     log = models.ForeignKey(OperationLog, on_delete=models.CASCADE, related_name='log_filename', null=True)
#     # 対象ファイル名/onetooneだと送るとき、それを消すときで重複してcreateできなかった
#     file = models.ForeignKey(Filemodel, on_delete=models.CASCADE, related_name='log_filename', null=True)
#     # file = models.OneToOneField(Filemodel, on_delete=models.CASCADE, related_name='log_filename', null=True)

# # 操作ログ用の宛先メールテーブル
# class LogDestUser(models.Model):
#     # 操作ログ紐づけ
#     log = models.ForeignKey(OperationLog, on_delete=models.CASCADE, related_name='log_destuser', null=True)
#     # ???
#     log_dest_user = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='log_destuser', null=True)

