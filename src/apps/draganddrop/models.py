from django.db import models
from django.conf import settings
from accounts.models import User, Service, Company
from contracts.models import Contract, Plan
import uuid
from datetime import date
from django.utils import timezone
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


class logtable(models.Model):
    user = models.CharField(max_length=245, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    file = models.ManyToManyField(Filemodel, verbose_name=('file'), blank=True)
    text = models.CharField(max_length=140)


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