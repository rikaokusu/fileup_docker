from django.db import models

from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
import os
# from django.conf import settings

# IDをUUID化
import uuid
from django.db import models

from .choices import LEGALPERSONALITY_CHOICES, PREFECTURES_CHOICES, LEGALPERSON_POSI_CHOICES,CORPCLASS_CHOICES,MIDDLE_CHOICES
from .choices import SMTP_CONNECTION_CHOICES

from django_mysql.models import ListCharField


"""
サービステーブル
"""
class Service(models.Model):
    #id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 表示名
    name = models.CharField('表示名', max_length=255, null=True)
    # 説明
    description = models.TextField('説明', blank=True, null=True)
    # イニシャル
    initial = models.CharField('頭文字', max_length=2, default='Z', blank=True, null=True)
    # アイコン
    icon = models.CharField('アイコン', max_length=255, default='', blank=True, null=True)
    # サービス番号
    number = models.CharField('番号', max_length=10, default='0', blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        managed = False

"""
会社テーブル
"""
class Company(models.Model):
    SETTING_CHOICES = (
        ('1','有効'),
        ('2','無効')
    )

    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 会社名
    pic_company_name = models.CharField('会社名', max_length=255)
    #法人・個人
    pic_corp_class = models.CharField('法人区分',max_length=2, choices=CORPCLASS_CHOICES,blank=True)
    # 法人格
    pic_legal_personality = models.CharField('法人格', max_length=2, choices=LEGALPERSONALITY_CHOICES, blank=True)
    # 法人格位置
    pic_legal_person_posi = models.CharField('法人格位置', max_length=1, choices=LEGALPERSON_POSI_CHOICES, blank=True)
    # 所属名
    pic_dept_name = models.CharField('所属名', max_length=150, blank=True)
    # 氏名
    pic_full_name = models.CharField('担当者名', max_length=255, blank=True)
    # 郵便番号
    postal_code_regex = RegexValidator(regex=r'^[0-9]+$', message = ("Postal Code must be entered in the format: '1234567'. Up to 7 digits allowed."))
    pic_post_code = models.CharField(validators=[postal_code_regex], blank=True, max_length=7, verbose_name='郵便番号')
    # 都道府県
    pic_prefectures = models.CharField('都道府県', max_length=2, choices=PREFECTURES_CHOICES, blank=False)
    # 住所
    pic_address = models.CharField('住所', max_length=255, blank=True)
    # 建物名称
    pic_building_name = models.CharField('建物名称', max_length=255, blank=True)
    # 電話番号
    tel_number_regex = RegexValidator(regex=r'^[0-9]+$', message = ("Tel Number must be entered in the format: '09012345678'. Up to 15 digits allowed."))
    pic_tel_number = models.CharField('電話番号', max_length=15,  blank=True, validators=[tel_number_regex])
    # 会社名
    invoice_company_name = models.CharField('会社名', max_length=255, blank=True)
    # 法人格
    invoice_legal_personality = models.CharField('法人格', max_length=2, choices=LEGALPERSONALITY_CHOICES, blank=True)
    # 法人格位置
    invoice_legal_person_posi = models.CharField('法人格位置', max_length=1, choices=LEGALPERSON_POSI_CHOICES, blank=True)
    # 所属名
    invoice_dept_name = models.CharField('所属名', max_length=150, blank=True)
    # 氏名
    invoice_full_name = models.CharField('請求者氏名', max_length=255, blank=True)
    # 郵便番号
    invoice_post_code = models.CharField(validators=[postal_code_regex], blank=True, max_length=7, verbose_name='郵便番号')
    # 都道府県
    invoice_prefectures = models.CharField('都道府県', max_length=2, choices=PREFECTURES_CHOICES, blank=False)
    # 住所
    invoice_address = models.CharField('住所', max_length=255, blank=True)
    # 建物名称
    invoice_building_name = models.CharField('建物名称', max_length=255, blank=True)
    # 電話番号
    invoice_tel_number = models.CharField('電話番号', max_length=15,  blank=True, null=True, validators=[tel_number_regex])
    # バージョン
    version = models.DateTimeField(_('version'), blank=True, null=True)
    # 変更者
    change_user = models.CharField('変更者ID', max_length=255, blank=True, null=True)
    # 上書きフラグ
    change_row = models.CharField('上書きフラグ', max_length=255, blank=True, null=True)
    #ミドルネーム選択
    middle_choice = models.BooleanField(_('middle_choice'), default=False)
    #パスワード変更
    pass_change = models.CharField('パスワード変更', max_length=2, choices=SETTING_CHOICES, default='2')
    #プロファイル変更
    profile_change = models.CharField('プロフィール変更', max_length=2, choices=SETTING_CHOICES, default='2')
    #ミドルネーム選択２
    # middle_choice2 = models.CharField('ミドルネームの使用', max_length=2, choices=MIDDLE_CHOICES, default='2')
    # メールサーバ
    # email_host = models.CharField('メールサーバ', max_length=50, blank=True, null=True)
    # メールサーバ
    # port = models.CharField('ポート番号', max_length=50, blank=True, null=True)
    # 認証ユーザー
    # host_user = models.CharField('認証ユーザ', max_length=50, blank=True, null=True)
    # 認証パスワード
    # host_password = models.CharField('認証パスワード', max_length=50, blank=True, null=True)
    # Fromアドレス
    # from_address = models.CharField('送信元アドレス', max_length=50, blank=True, null=True)
    # 通信タイプ
    # smtp_connection_type = models.CharField('法人格', max_length=2, choices=SMTP_CONNECTION_CHOICES, blank=True, default=1)

    def __str__(self):
        return self.pic_company_name

class Meta:
        managed = False
"""
ユーザーやスーパーユーザーを作成するためのメソッド
"UserCreationForm"を継承したFormを使うことでこの
メソッドを通してユーザーが作成できる。
その結果、Djangoで用意されているパスワードのハッシュ化や
バリデーションが利用できるようになる
"""
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
"""
ファイルテーブル
"""
class File(models.Model):
    file = models.FileField(_('file'), upload_to='uploads/', null=True, blank=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    size = models.CharField(_('size'), max_length=255, blank=True)
    def __str__(self):
        return self.name

"""
カスタムユーザーテーブル
既存のUserを継承する形で独自のフィールドや設定を加えた
ユーザーテーブル
"""
class User(AbstractBaseUser, PermissionsMixin):
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 表示名
    display_name = models.CharField('表示名', max_length=30, blank=True, null=True)
    # メールアドレス
    email = models.CharField(_('email address'), unique=True, max_length=255)
    # サブドメイン
    subdomain = models.CharField(_('subdomain'), max_length=50, blank=True)
    # 姓
    last_name = models.CharField(_('last name'), max_length=20, blank=True)
    # ミドルネーム
    middle_name = models.CharField('ミドルネーム', max_length=20, blank=True)
    # 名
    first_name = models.CharField(_('first name'), max_length=20, blank=True)
    # ふりがな表示名
    p_display_name = models.CharField('ふりがな(表示名)', max_length=50, blank=True, null=True)
    # ふりがな(姓)
    p_last_name = models.CharField('ふりがな(姓)', max_length=30, blank=True, null=True)
    # ふりがな(名)
    p_first_name = models.CharField('ふりがな(名)', max_length=30, blank=True, null=True)
    # ふりがな(ミドルネーム)
    p_middle_name = models.CharField('ふりがな(ミドルネーム)', max_length=30, blank=True)
    # 所属グループ
    # group = models.ManyToManyField(CustomGroup, verbose_name="所属グループ", blank=True)
    # 説明
    description = models.CharField('メモ', max_length=30, blank=True)
    # 会社コード
    company = models.ForeignKey(Company, null=True, on_delete=models.PROTECT)
    # サービス
    service = models.ManyToManyField(Service, verbose_name="利用サービス", blank=True, related_name='service')
    # サービス管理者
    service_admin = models.ManyToManyField(Service, verbose_name="サービス管理者", blank=True, related_name='service_admin')
    # 登録ユーザー(タスクサービスでユーザー一覧の抽出時に使用)
    # reg_user = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    # 契約外ユーザーのフラグ
    # is_nocontract = models.BooleanField(_('no contract'), default=False)
    # 作成日
    created_date = models.DateTimeField(_('created date'), default=timezone.now)
    # pay.jpのID
    # payjp_cus_id = models.CharField('PAY.JPのカスタマーID', max_length=35, blank=True, null=True)
    # メール送信可否
    is_send_mail = models.BooleanField(_('is_send_mail'), default=True)
    # プロフィール写真
    image = models.OneToOneField(File, on_delete=models.CASCADE,blank=True,null=True)
    # ユーザーカラー
    color_num = models.IntegerField("color_num", default=0,blank=True)

    is_activate = models.BooleanField(
        _('activate'),
        default=False,
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
    )
    # ステータス
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )

    # 論理的削除
    is_rogical_deleted = models.BooleanField(
        _('rogical_deleted'),
        default=False,
    )


    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        managed = False

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.last_name, self.first_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        if self.display_name:
            name = self.display_name + " / " + self.email
        else:
            name = self.email
        return name


    @property
    def username(self):
        """
        username属性のゲッター
        他アプリケーションが、username属性にアクセスした場合に備えて定義メールアドレスを返す
        """
        return self.email

"""
メッセージ(トースト)管理テーブル
"""
class Messages(models.Model):
    # 表示対象者
    user = models.CharField('対象者', max_length=255, blank=True, null=True)
    # url
    url = models.CharField('url', max_length=255, blank=True, null=True)
    # カテゴリ
    category = models.CharField(_('category'), max_length=20, blank=True, null=True)
    # メッセージ
    text = models.CharField(_('text'), max_length=255, blank=True, null=True)
    # チェック有無
    checked = models.BooleanField(_('checked'), default=False)

    class Meta:
        managed = False
# """
# リマインダー
# """
# class Notification(models.Model):
#     # ID
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     release_date = models.DateTimeField(_('release date'), default=timezone.now, blank=True)
#     title = models.CharField(_('title'), max_length=255)
#     category = models.CharField(_('category'), max_length=255, default="お知らせ")
#     target_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='target_user')
#     is_read = models.BooleanField(_('is_read'), default=False)
#     # 通知開始日
#     start_date = models.DateTimeField(_('start date'), default=timezone.now, blank=True)
#     #内容
#     contents = models.TextField('内容', blank=True, null=True)

"""
Stripe情報
"""
class Stripe(models.Model):
    # ユーザー
    # user = models.OneToOneField(User, null=False, on_delete=models.CASCADE, default='')
    # stripeのカスタマーID
    stripe_cus_id = models.CharField('StripeのカスタマーID', max_length=35, blank=True, null=True)
    # stripeのCardーID
    stripe_card_id = models.CharField('StripeのCardID', max_length=35, blank=True, null=True)
    # 会社コード
    company = models.OneToOneField(Company, null=True, on_delete=models.CASCADE, default='')

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                            各アプリごとのユーザー・管理者権限詳細テーブル
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""
FileUP用サービス権限
"""
class FileupPermissions(models.Model):
    FILEUPPERMISSION_CHOICES = (
            ('0', '一般ユーザー'),
            ('1', '管理者１'),
            ('2', '管理者２'),
            ('3', '管理者３'),
            ('4', '管理者４'),
            ('5', '管理者５'),
            ('6', '管理者６'),
            ('7', '管理者７'),
            ('8', '管理者８'),
            ('9', '管理者９'),
            ('10', '管理者１０')
    )
    # ユーザー
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, default="")
    # 各機能権限
    permission = models.CharField(max_length=2, default=0, choices=FILEUPPERMISSION_CHOICES, blank=True)
    # 管理者権限有無（デフォルトは一般ユーザーであるFalse）
    admin = models.BooleanField('管理者権限有無',default=False)
    # 各機能権限１
    role1 = models.BooleanField('各機能権限１',default=False)
    # 各機能権限２
    role2 = models.BooleanField('各機能権限２',default=False)
    # 各機能権限３
    role3 = models.BooleanField('各機能権限３',default=False)
    # 各機能権限４
    role4 = models.BooleanField('各機能権限４',default=False)
    # 各機能権限５
    role5 = models.BooleanField('各機能権限５',default=False)



"""
リマインダー
"""
class Notification(models.Model):

    CATEGORY_CHOICES = (
            ('お知らせ', 'お知らせ'),
            ('メッセージ', 'メッセージ'),
            ('メンテナンス', 'メンテナンス'),
            ('メンテナンス終了', 'メンテナンス終了'),
            ('メンテナンス中止', 'メンテナンス中止'),
            ('受信通知','受信通知')
    )
    SERVICE_CHOICES = (
        ('全てのサービス', '全てのサービス'),
        ('ポータル','ポータル'),
        ('FileUP!','FileUP!'),
        ('まなもあ','まなもあ'),
        ('Kolette','Kolette')
    )
    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #サービス名
    service = models.CharField(_('service'),null=True,choices=SERVICE_CHOICES,max_length=255)
    #会社紐づけ
    company = models.ForeignKey(Company,blank=True, null=True,on_delete=models.CASCADE, related_name='target_company')
    #会社名リスト
    company_list = models.TextField(null=True,blank=True)
    #送信者(CL運営者、ログインユーザー)
    sender = models.CharField(_('sender'),null=True,max_length=30)
    #送信日？
    release_date = models.DateTimeField(_('release date'), default=timezone.now, blank=True)
    #タイトル、件名
    title = models.CharField(_('title'), max_length=255)
    #カテゴリ（お知らせ、メンテナンス）
    category = models.CharField(_('category'), max_length=30, default="1", choices=CATEGORY_CHOICES, blank=False)
    # category = models.CharField(_('category'), max_length=255, default="お知らせ")
    target_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='target_user')
    # ユーザーemailリスト
    email_list = models.TextField(null=True,blank=True)
    #ユーザー種別
    user_category = models.TextField(null=True,blank=True)
    # 通知開始日
    start_date = models.DateTimeField(_('start date'), default=timezone.now, blank=True)
    #内容
    contents = models.TextField('内容', blank=True, null=True)
    #メンテナンス情報（作業開始日時）
    maintenance_start_date = models.DateTimeField(_('メンテナンス開始日時'), default=timezone.now, blank=True)
    #メンテナンス情報（作業終了日時）
    maintenance_end_date = models.DateTimeField(_('メンテナンス終了日時'), default=timezone.now, blank=True)
    #メンテナンス情報（作業内容）
    maintenance_contents = models.TextField('作業内容', blank=True, null=True)
    #メンテナンス情報（作業対象）
    maintenance_targets = models.CharField(_('service'),null=True,choices=SERVICE_CHOICES,max_length=255)
    # maintenance_targets = models.TextField('作業対象', blank=True, null=True)
    #メンテナンス情報（作業影響）
    maintenance_affects = models.TextField('作業影響', blank=True, null=True)
    #メンテナンス情報（作業中止理由）
    maintenance_cancel_reason = models.TextField('作業中止理由', blank=True, null=True)
    #FileUP用ファイルタイトル
    fileup_title = models.TextField('ファイルタイトル', blank=True, null=True)
    
    class Meta:
        managed = False

"""
お知らせ既読管理
"""
class Read(models.Model):
    # ユーザー
    read_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='read_user')
    # 既読日
    read_date = models.DateTimeField(_('read date'), default=timezone.now, blank=True)
    # お知らせID
    notification_id = models.ForeignKey(Notification, blank=True, null=True, on_delete=models.CASCADE, related_name='notification_id')

    class Meta:
        managed = False