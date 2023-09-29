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
    # サービス
    service = models.ForeignKey(Service, null=False, on_delete=models.CASCADE, default=1)
    # PAY.JPのプランID
    payjp_plan_id = models.CharField('PAY.JPのプランID', max_length=35, blank=False, default="pln")
    # 名前
    name = models.CharField('プラン名', max_length=30, blank=False)
    # 料金(年額)
    price = models.IntegerField('価格', blank=True, default=0)
    # 単価(月額)
    unit_price = models.IntegerField('価格(単価)', blank=True, default=0)
    # 説明
    description = models.TextField('説明', blank=True)
    # ユーザー数
    user_num = models.IntegerField('ユーザー数', blank=True, default=0)
    # カテゴリー
    category = models.CharField('カテゴリー', max_length=30, default="なし")
    # オプションフラグ
    is_option = models.BooleanField(default=False, blank=True)
    # 試用フラグ
    is_trial = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name



"""
契約テーブル
"""
class Contract(models.Model):

    STATUS_CHOICES = (
            ('1', '試用'),
            ('2', '本番'),
            ('3', '解約'),
    )

    # ユーザー
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, default="")
    # user = models.CharField('契約者', max_length=255, blank=True, null=True)
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
    # option = models.ManyToManyField(Plan, blank=True, verbose_name='オプション', related_name='contract_option')
    option = models.CharField('オプション', max_length=10, blank=True, null=True)
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


