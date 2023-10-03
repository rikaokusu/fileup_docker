from django.db import models

from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
import os
from django.conf import settings

# IDをUUID化
import uuid
from django.db import models

from accounts.models import User, Company, Messages, Service



"""
プランテーブル
"""
class Plan(models.Model):
    #id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # サービス
    service = models.ForeignKey(Service, null=False, on_delete=models.CASCADE, default=1)
    # 名前
    name = models.CharField('プラン名', max_length=30, blank=False)
    # 料金(年額)
    price = models.IntegerField('価格', blank=True, default=0)
    # 単価(月額)
    unit_price = models.IntegerField('価格(単価)', blank=True, default=0)
    # 説明
    description = models.TextField('説明', blank=True)
    # ユーザー数
    # user_num = models.IntegerField('ユーザー数', blank=True, default=0)
    # カテゴリー
    category = models.CharField('カテゴリー', max_length=30, default="なし")
    # オプションフラグ
    is_option = models.BooleanField(default=False, blank=True)
    # 試用フラグ
    is_trial = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

"""
プラン・オプション詳細テーブル【FileUp!】
"""
class FileupDetail(models.Model):
    #　id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # プランまたはオプション
    plan = models.ForeignKey(Plan, null=False, on_delete=models.CASCADE, default=1)
    # 契約人数上限
    user_limit = models.IntegerField('ユーザー上限', blank=True, null=True)
    # 使用可能容量
    capacity = models.IntegerField('使用可能容量', null=True, blank=True)
    # URL共有
    url_share = models.BooleanField('URL共有可否',null=True, blank=True)
    # 管理
    manage = models.BooleanField('管理',null=True, blank=True)
    # DL期限
    dl_limit = models.IntegerField('DL期限', null=True, blank=True)
    # 件数上限
    max_items = models.IntegerField('件数上限', null=True, blank=True)
    # ワンタイムパスワード設定
    one_time_pw = models.BooleanField('ワンタイムパスワード設定可否', null=True, blank=True)

"""
契約テーブル
"""
class Contract(models.Model):

    STATUS_CHOICES = (
            ('1', '試用'),
            ('2', '本番'),
            ('3', '解約'),
            ('4', '旧契約'),
            ('5','振込前'),
            ('6','振込通知済み')
    )
    #ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ユーザー
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, default="")
    # 会社
    company = models.ForeignKey(Company, null=False, on_delete=models.CASCADE, default="")
    # サービス
    service = models.ForeignKey(Service, null=False, on_delete=models.CASCADE, default=1)
    # service = models.CharField('サービス', max_length=10, blank=True, null=True)
    # ステータス(試用、本番)
    status = models.CharField(_('status'), max_length=1, choices=STATUS_CHOICES, blank=True)
    # 契約開始日(試用、本番)
    contract_start_date = models.DateTimeField(_('contract start date'), null=True)
    # 契約終了日(試用、本番）
    contract_end_date = models.DateTimeField(_('contract end date'), null=True)
    # 支払い開始日(試用、本番)
    pay_start_date = models.DateTimeField(_('pay start date'), null=True)
    # 支払い終了日(試用、本番）
    pay_end_date = models.DateTimeField(_('pay end date'), null=True)
    # 紐づく見積
    # estimate = models.ManyToManyField(Estimates, verbose_name="見積もり", blank=True)
    # 紐づく支払い(※循環インポートを避けるためクラス名から指定)
    # payment = models.ForeignKey('payment.Payment', null=True, default="", on_delete=models.CASCADE)
    # プラン
    plan = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='プラン', related_name='contract_plan')
    # オプション
    # option = models.CharField('オプション', max_length=10, blank=True, null=True)
    # オプション1
    option1 = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='オプション1', default="", related_name='contract_option1')
    # オプション2
    option2 = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='オプション2', default="", related_name='contract_option2')
    # オプション3
    option3 = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='オプション3', default="", related_name='contract_option3')
    # オプション4
    option4 = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='オプション4', default="", related_name='contract_option4')
    # オプション5
    option5 = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE, verbose_name='オプション5', default="", related_name='contract_option5')

    # 小計
    minor_total = models.IntegerField('小計', blank=False, default=0)
    # 消費税
    tax = models.IntegerField('消費税', blank=False, default=0)
    # 合計
    total = models.IntegerField('合計', blank=False, default=0)
    # 自動更新の有効・無効
    is_autocheckout = models.BooleanField(null=True)
    # 請求書オプションフラグ
    is_invoice_need = models.BooleanField('請求書オプションフラグ', blank=True, default=False)
    # 請求書オプション割引
    # invoice_op_discount = models.IntegerField('請求書オプション割引', blank=True, default='-3000')



