from django import forms
from .models import User, Company, Service
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, PasswordChangeForm, AdminPasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from betterforms.multiform import MultiModelForm

# 翻訳
from django.utils.translation import gettext_lazy as _

# 正規表現
import re

# nslookup
import socket

# 日付カレンダー表示
# import bootstrap_datepicker_plus as datetimepicker

# DBのカウント(サービステーブルから契約テーブルの数を計算する際に使用)
from django.db.models import Count, Q

# 正規表現用ファイルの読み込み
from .lib.regcreate import regcreate
from .lib.regcreate_white import regcreate_white


# 逆参照のテーブルをフィルタやソートする
from django.db.models import Prefetch

# 時間を扱う
import datetime



"""
ログイン画面のフォーム
"""
class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                パスワードを忘れた方
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""
パスワード変更フォーム（old password あり）
ユーザーが自身のパスワードを変更する際に使用
"""
class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
"""
パスワードリセットフォーム
ユーザーが自身のパスワードをリセットする際に使用
"""
class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'






"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                    ユーザー管理関連
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""





"""
宛先ユーザーのチェックボックスの見た目をカスタマイズするためのウィジェット
"""
class Service_Admin_Checkbox(forms.CheckboxSelectMultiple):
    input_type = 'checkbox'
    template_name = 'accounts/forms/widget/service_admin_checkbox.html'
    def get_context(self, name, value, attrs):
            service_initial_name_list = []
            service_contract_count_list = []

            context = super(Service_Admin_Checkbox, self).get_context(name, value, attrs)
            services = Service.objects.all().annotate(num_contract=Count('contract', filter=Q(contract__user_id=self.attrs['user_id'])))
            # services = Service.objects.all()

            for service in services:
                # サービス毎の頭文字をリストへ追加
                service_initial_name = service.initial
                service_initial_name_list.append(service_initial_name)

                # サービス毎の契約状況を調査。契約状況にログインユーザーの存在を確認してカウントアップする(0=は未契約、1以上は契約)
                service_contract_count = service.num_contract
                service_contract_count_list.append(service_contract_count)


            context['service_initial_name_list'] = service_initial_name_list
            context['service_contract_count_list'] = service_contract_count_list

            return context

"""
宛先ユーザーのチェックボックスの見た目をカスタマイズするためのウィジェット
"""
class Service_Checkbox(forms.CheckboxSelectMultiple):
    input_type = 'checkbox'
    template_name = 'accounts/forms/widget/service_checkbox.html'
    def get_context(self, name, value, attrs):
            service_initial_name_list = []
            service_contract_count_list = []
            service_contract_user_count_list = []
            service_contract_user_count_dict = {}
            service_contracted_user_count_list = {}

            context = super(Service_Checkbox, self).get_context(name, value, attrs)
            services = Service.objects.all().annotate(num_contract=Count('contract', filter=Q(contract__user_id=self.attrs['user_id'])))
            # services = Service.objects.all()
            # contracts = Contract.objects.filter(user = self.attrs['user_id']).select_related('plan')
            myself = User.objects.get(id = self.attrs['user_id'])


            for service in services:
                # サービス毎の頭文字をリストへ追加
                service_initial_name = service.initial
                service_initial_name_list.append(service_initial_name)

                # サービス毎の契約状況を調査。契約状況にログインユーザーの存在を確認してカウントアップする(0=は未契約、1以上は契約)
                service_contract_count = service.num_contract
                service_contract_count_list.append(service_contract_count)

                # サービスの利用済みユーザー数を登録
                service_contracted_user_count_list[service.name] = (User.objects.filter(company = myself.company, service__name=service.name).count())

            # # サービスプランのユーザーオプションの契約数
            # for contract in contracts:
            #     # 本契約の処理
            #     if contract.status == "2":
            #         # 2回めのループのためにクリア
            #         service_contract_user_count_list.clear()
            #         # プランに設定されたユーザー数を追加
            #         # service_contract_user_count_list.append(contract.plan.user_num)

            #         # if contract.usernum is not None:
            #             # オプションに設定されたユーザー数を追加
            #             # service_contract_user_count_list.append(contract.usernum.user_num)

            #         # プランとオプションに設定されたユーザー数の合計値
            #         service_contract_user_count_dict[contract.service.name] = sum(service_contract_user_count_list)

            #     # 仮契約の処理
            #     elif contract.status == "1":
            #         service_contract_user_count_dict[contract.service.name] = "0(仮登録)"


            context['service_initial_name_list'] = service_initial_name_list
            context['service_contract_count_list'] = service_contract_count_list
            context['service_contract_user_count_dict'] = service_contract_user_count_dict
            context['service_contracted_user_count_list'] = service_contracted_user_count_list

            return context




"""
管理者がユーザーを登録する画面のフォーム　
UserChangenFormを継承してCreate_Userが使われるようにする。
"""
class MyUserCreationForm(UserCreationForm):
    domain_check = forms.BooleanField(label='サブドメイン(任意)', required=False, widget=forms.CheckboxInput(attrs={'class': 'check'},))
    # 管理者が作成する画面ではパスワードは必須としない(自動的にランダムなパスワードをセットする)
    password1 = forms.CharField(label='パスワード', required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワードの確認', required=False, widget=forms.PasswordInput)
    last_name = forms.CharField(label='姓', required=True)
    first_name = forms.CharField(label='名', required=True)
    email  = forms.CharField(label='メールアドレス', required=True)
    subdomain  = forms.CharField(label='サブドメイン', required=False)
    is_staff  = forms.BooleanField(label='管理者', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['service'] = forms.ModelMultipleChoiceField(label="利用サービス",
                                                                # Service_Checkboxにuser_idを渡し、Service_Checkbox側で、サービスの契約状況をフィルタする際の条件で利用
                                                                widget=Service_Checkbox(attrs = {'user_id': self.user.id}),
                                                                queryset=Service.objects.annotate(num_contract=Count('contract', filter=Q(contract__user_id=self.user))),
                                                                # queryset=Service.objects.all(),
                                                                required=False,
                                                            )

        self.fields['service_admin'] = forms.ModelMultipleChoiceField(label="サービス管理者",
                                                                # Service_Checkboxにuser_idを渡し、Service_Checkbox側で、サービスの契約状況をフィルタする際の条件で利用
                                                                widget=Service_Admin_Checkbox(attrs = {'user_id': self.user.id}),
                                                                # queryset=Service.objects.annotate(num_contract=Count('contract', filter=Q(contract__user_id=self.user))),
                                                                queryset=Service.objects.all(),
                                                                required=False,
                                                            )

    class Meta:
        model = User
        fields = ('domain_check', 'email', 'subdomain', 'last_name', 'first_name', 'p_last_name', 'p_first_name', 'description', 'is_staff', 'service_admin',)



    def clean(self):
        cleaned_data = super(MyUserCreationForm, self).clean()

        user_name = self.cleaned_data['email']
        subdomain = self.cleaned_data['subdomain']

        #　ログインユーザーのを取得してメールアドレスを
        current_user = self.user
        # メールアドレスをユーザ名とドメインに分割
        domain = current_user.email.rsplit('@', 1)[1]

        is_checked = self.cleaned_data['domain_check']

        if is_checked:
            email = user_name + "@" + subdomain + "." + domain
        else:
            email = user_name + "@" + domain

        is_exist_email = User.objects.filter(email = email).exists()

        if is_exist_email:
            raise forms.ValidationError(
                'このメールアドレスは使用できません。'
            )



"""
パスワード変更フォーム（old password なし）
ユーザーが本登録時にパスワードを設定する際と管理者がユーザーのパスワードを変更するときに使用
"""
class CustomPasswordChangeForm(AdminPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



"""
管理者がユーザーを編集する画面のフォーム
UserChangenFormを継承してCreate_Userが使われるようにする。
"""
class MyUserChangeForm(UserChangeForm):

    last_name = forms.CharField(label='姓', required=True)
    first_name = forms.CharField(label='名', required=True)

    class Meta:
        model = User
        fields = ('email', 'last_name', 'first_name', 'p_last_name', 'p_first_name', 'service', 'description', 'is_staff', 'service_admin',)
        exclude = ('password',)

    def clean_password(self):
        return "" # This is a temporary fix for a django 1.4 bug　パスワードのKeyエラーになる

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MyUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['service'] = forms.ModelMultipleChoiceField(label="利用サービス",
                                                                # Service_Checkboxにuser_idを渡し、Service_Checkbox側で、サービスの契約状況をフィルタする際の条件で利用
                                                                widget=Service_Checkbox(attrs = {'user_id': self.user.id}),
                                                                queryset=Service.objects.annotate(num_contract=Count('contract', filter=Q(contract__user_id=self.user))),
                                                                required=False,
                                                            )

        self.fields['service_admin'] = forms.ModelMultipleChoiceField(label="サービス管理者",
                                                                # Service_Checkboxにuser_idを渡し、Service_Checkbox側で、サービスの契約状況をフィルタする際の条件で利用
                                                                widget=Service_Admin_Checkbox(attrs = {'user_id': self.user.id}),
                                                                queryset=Service.objects.annotate(num_contract=Count('contract', filter=Q(contract__user_id=self.user))),
                                                                required=False,
                                                            )











"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                管理者登録(初めてのかた)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""






"""
ユーザーの仮登録用フォーム
"""
class UserRegForm(UserCreationForm):
    email = forms.CharField(label="メールアドレス")
    password1 = forms.CharField(label="パスワード", widget=forms.PasswordInput)
    password2 = forms.CharField(label="パスワードの確認", widget=forms.PasswordInput)
    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email',)
        else:
            fields = ('username', 'email')






"""
法人格位置の選択肢
"""
LEGALPERSON_POSI_CHOICES = (
    ('1', '前'),
    ('2', '後')
)

"""
法人区分の選択肢
"""
CORPCLASS_CHOICES = (
    ('1', '法人'),
    ('2', '個人')
)


"""
法人格位置の見た目をカスタマイズするためのウィジェット
"""
class Legal_Person_Posi_Radio(forms.RadioSelect):
    input_type = 'radio'
    template_name = 'accounts/forms/widget/legal_person_posi.html'



"""
法人区分の見た目をカスタマイズするためのウィジェット
"""
class Corp_Class_Radio(forms.RadioSelect):
    input_type = 'radio'
    template_name = 'accounts/forms/widget/corp_class_radio.html'




"""
会社の仮登録用フォーム
"""
class CompanyRegForm(forms.ModelForm):
    pic_company_name = forms.CharField(label="会社名")
    # pic_kojincheck = forms.BooleanField(label='個人事業主', required=False, widget=forms.CheckboxInput(attrs={'class': 'check'}),)
    pic_corp_class = forms.ChoiceField(label='法人区分', required=False, widget=Corp_Class_Radio(), choices=CORPCLASS_CHOICES,)
    pic_legal_person_posi = forms.ChoiceField(label='法人格位置', required=False, widget=Legal_Person_Posi_Radio(), choices=LEGALPERSON_POSI_CHOICES,)
    pic_dept_name = forms.CharField(label="所属名", required=False)
    class Meta:
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['pic_dept_name'].help_text = '<br/>Hold down "Control" to select more.'

        model = Company
        fields = ('pic_company_name', 'pic_legal_person_posi', 'pic_dept_name', 'pic_legal_personality')




"""
ユーザーと会社の仮登録用フォーム
(MultiModelForm)
"""
class UserCompanyMultiForm(MultiModelForm):
    form_classes = {
        'company': CompanyRegForm,
        'user': UserRegForm,
    }



    def clean(self):
        cleaned_data = super(UserCompanyMultiForm, self).clean()

        # フィールドのバリデーションでユニークTrueとなっているためcleaned_dataに値が入らず、重複している場合はNoneとなる
        if cleaned_data.get('user') == None:
            raise forms.ValidationError(
                'このメールアドレスは使用できません。'
            )

        try:

            company_name = cleaned_data.get('company')['pic_company_name']
            dept_name = cleaned_data.get('company')['pic_dept_name']
            email = cleaned_data.get('user')['email']

            is_match = re.match(regcreate(), email)

            if is_match:
                raise forms.ValidationError(
                    'このメールアドレスは使用できません。'
                )
            else:
                # メールアドレスからドメインのみ取得
                domain = email.rsplit('@', 1)[1]

                try:
                    # ホワイトリストと比較
                    is_match = re.match(regcreate_white(), email)

                    if is_match:
                        # ホワイトリストにあった場合、MXチェック
                        ip = socket.gethostbyname(domain)

                    else:
                        # ホワイトリストになかった場合エラー
                        raise forms.ValidationError(
                            'このメールアドレスは使用できません。'
                        )

                except:
                    # 何かしらで失敗した場合
                    raise forms.ValidationError(
                        '有効なメールアドレスを入力してください。'
                    )

            # メールアドレスからドメインのみ取得
            domain = email.rsplit('@', 1)[1]


        except Exception as e:
            raise forms.ValidationError(e)


        num_users = User.objects.all().filter(email__contains=domain,
                                        company__pic_company_name=company_name,
                                        company__pic_dept_name=dept_name).count()


        if not num_users == 0:
            if not dept_name:
                raise forms.ValidationError(
                    company_name + 'は既にすでに契約済みです。'
                    'ご担当者様へご確認ください。'
                )
            else:
                raise forms.ValidationError(
                    company_name + 'の' + dept_name + 'は既にすでに契約済みです。'
                    'ご担当者様へご確認ください。'

                )

        return cleaned_data






"""
本番登録後のユーザー情報追加フォーム
(パスワードとユーザ名の変更が不要なのでModelFormを利用)
"""
class UserAddInfoForm(forms.ModelForm):

    last_name = forms.CharField(label="姓", required=True)
    first_name = forms.CharField(label='名', required=True)
    p_last_name = forms.CharField(label="ふりがな(姓)", required=False)
    p_first_name = forms.CharField(label='ふりがな(名)', required=False)


    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'p_first_name', 'p_last_name', )





"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                    会社更新
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



"""
会社情報変更フォーム
"""
class CompanyUpdateForm(forms.ModelForm):


    pic_company_name = forms.CharField(label="会社名", required=True)
    pic_legal_person_posi = forms.ChoiceField(label='法人格位置', required=False, widget=Legal_Person_Posi_Radio(), choices=LEGALPERSON_POSI_CHOICES,)
    pic_full_name = forms.CharField(label='氏名', required=True)
    pic_post_code = forms.CharField(label="郵便番号", required=True)
    pic_address = forms.CharField(label='住所', required=True)
    pic_tel_number = forms.CharField(label='電話番号', required=True)

    invoice_company_name = forms.CharField(label="会社名", required=True)
    invoice_legal_person_posi = forms.ChoiceField(label='法人格位置', required=False, widget=Legal_Person_Posi_Radio(), choices=LEGALPERSON_POSI_CHOICES,)
    invoice_full_name = forms.CharField(label='氏名', required=True)
    invoice_post_code = forms.CharField(label="郵便番号", required=True)
    invoice_address = forms.CharField(label='住所', required=True)
    invoice_tel_number = forms.CharField(label='電話番号', required=True)

    class Meta:
        model = Company
        fields = ('pic_company_name', 'pic_legal_personality', 'pic_legal_person_posi', 'pic_dept_name', 'pic_full_name', 'pic_post_code', 'pic_prefectures', 'pic_address', 'pic_building_name', 'pic_tel_number', 'invoice_company_name', 'invoice_legal_personality', 'invoice_legal_person_posi', 'invoice_dept_name', 'invoice_full_name', 'invoice_post_code', 'invoice_prefectures', 'invoice_address', 'invoice_building_name', 'invoice_tel_number',)

