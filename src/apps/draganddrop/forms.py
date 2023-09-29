from django.forms import ModelForm
from django import forms
from draganddrop.models import Filemodel, UploadManage, Address, Group, UrlUploadManage
from accounts.models import User
import bootstrap_datepicker_plus as datetimepicker
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm

# 日付
import datetime


class FileForm(ModelForm):
    class Meta:
        model = Filemodel
        fields = ('size', 'name', 'upload')


# データ管理step1
class User_Checkbox(forms.CheckboxSelectMultiple):
    input_type = 'checkbox'
    template_name = 'forms/widget/user_checkbox.html'


"""
法人区分の見た目をカスタマイズするためのウィジェット
"""


class Corp_Class_Radio(forms.RadioSelect):
    input_type = 'radio'
    template_name = 'forms/widget/corp_class_radio.html'


CHOICE = [
    ('1', '法人'),
    ('2', '個人'),
]

Legal_Personality = [
    ('0', ''),
    ('1', '株式会社'),
    ('2', '合同会社'),
    ('3', '合資会社'),
    ('4', '合名会社'),
]

Legal_Person_Posi = [
    ('1', '前'),
    ('2', '後'),
]

Number = [
    ('1', '1回'),
    ('2', '2回'),
    ('3', '3回'),
    ('4', '4回'),
    ('5', '5回'),
    ('99', '無期限'),
]


class ManageTasksStep1Form(forms.ModelForm):

    dest_user = forms.ModelMultipleChoiceField(
        queryset=Address.objects.all(),
        widget=User_Checkbox, required=False)

    dest_user_group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=User_Checkbox, required=False)

    end_date = forms.DateTimeField(required=True, label="DL期間", widget=datetimepicker.DateTimePickerInput(format='%Y/%m/%d %H:%M:%S',
        options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
                'minDate': (datetime.datetime.today() + datetime.timedelta(days=0)).strftime('%Y-%m-%d 00:00:00'),
                # 'maxDate': (datetime.datetime.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d 23:59:59'),
                # 'enabledHours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        }),
        input_formats=['%Y/%m/%d %H:%M:%S'])

    dl_limit = forms.ChoiceField(
        widget=forms.widgets.Select, choices=Number, initial=3)

    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows":3}), required=False)

    class Meta:
        model = UploadManage
        fields = (
            'dest_user',
            'dest_user_group',
            'dest_user_mail1',
            'dest_user_mail2',
            'dest_user_mail3',
            'dest_user_mail4',
            'dest_user_mail5',
            'dest_user_mail6',
            'dest_user_mail7',
            'dest_user_mail8',
            'end_date',
            'dl_limit',
            'title',
            'message'
        )
        error_messages = {
            'end_date': {
                'required': '必須です!',
            }}

    def __init__(self, *args, **kwargs):
        # Viewからログインユーザーを取得
        self.user = kwargs.pop('user', None)
        self.url = kwargs.pop('url', None)
        super(ManageTasksStep1Form, self).__init__(*args, **kwargs)

    def clean_title(self):

        # ログインユーザーと同じ会社のユーザーidを取得
        created_user = []
        users = User.objects.filter(company=self.user.company.id)
        for user in users:
           created_user.append(user.id)

        # formに入力された値を取得
        title = self.cleaned_data['title']
        # タイトル制限
        if self.url != "step1_update" :
            upload_manages = UploadManage.objects.filter(created_user__in=created_user).all()
            for upload_manage in upload_manages:
                if upload_manage.tmp_flag == 0:
                    if upload_manage.title == title:
                        raise forms.ValidationError(
                            mark_safe('同じタイトルが既に存在しています。'))
        return title


class DistFileUploadForm(forms.ModelForm):

    class Meta:
        model = UploadManage
        fields = ('file',)


class DummyForm(forms.Form):

    dummy = forms.DateTimeField(required=False, label="クローズ日時",
                                widget=datetimepicker.DateTimePickerInput(format='%Y/%m/%d',
                                                                          options={'locale': 'ja', 'dayViewHeaderFormat': 'YYYY年 MMMM', }),
                                input_formats=['%Y/%m/%d']),


class AddressForm(forms.ModelForm):

    legal_or_individual = forms.ChoiceField(
        label='種別', widget=Corp_Class_Radio(), initial=1, choices=CHOICE)
    legal_personality = forms.ChoiceField(
        label='法人格', widget=forms.widgets.Select, initial=1, choices=Legal_Personality, required=False)
    legal_person_posi = forms.ChoiceField(label='法人格 前後', widget=Corp_Class_Radio(
    ), choices=Legal_Person_Posi, initial=1, required=False)

    class Meta:
        model = Address
        fields = (
            'legal_or_individual',
            'legal_personality',
            'legal_person_posi',
            'company_name',
            'trade_name',
            'department_name',
            'last_name',
            'first_name',
            'email',
            'full_name_preview',
        )
        error_messages = {
            'company_name': {
                'required': '必須です!',
            }}


# データ管理
class Group_Checkbox(forms.CheckboxSelectMultiple):
    input_type = 'checkbox'
    template_name = 'forms/widget/user_checkbox.html'


class GroupForm(forms.ModelForm):
    group_name = forms.CharField(required=True) 
    address = forms.ModelMultipleChoiceField(
        queryset=Address.objects.all(),
        widget=User_Checkbox)

    class Meta:
        model = Group
        fields = (
            "group_name",
            "address"
        )
        error_messages = {
            'group_name': {
                'required': 'グループ名を記入してください',
            }}


class ManageTasksUrlStep1Form(forms.ModelForm):

    CHOICES = [
        ('1', 'メールアドレス'),
        ('2', 'メールアドレスとパスワード'),
    ]


    dest_user = forms.ModelMultipleChoiceField(
        queryset=Address.objects.all(),
        widget=User_Checkbox, required=False)

    dest_user_group = forms.ModelMultipleChoiceField(
            queryset=Group.objects.all(),
            widget=User_Checkbox, required=False)

    end_date = forms.DateTimeField(required=True, label="DL期間", widget=datetimepicker.DateTimePickerInput(format='%Y/%m/%d %H:%M:%S',
        options={
            'locale': 'ja',
            'dayViewHeaderFormat': 'YYYY年 MMMM',
            'minDate': (datetime.datetime.today() + datetime.timedelta(days=0)).strftime('%Y-%m-%d 00:00:00'),
            # 'maxDate': (datetime.datetime.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d 23:59:59'),
            # 'enabledHours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        }),
        input_formats=['%Y/%m/%d %H:%M:%S'])

    auth_meth = forms.ChoiceField(
        widget=forms.widgets.RadioSelect, choices=CHOICES, initial=1)

    dl_limit = forms.ChoiceField(
        widget=forms.widgets.Select, choices=Number, initial=3)

    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows":3}), required=False)

    class Meta:
        model = UrlUploadManage
        fields = (
            'title',
            'dest_user',
            'dest_user_group',
            'dest_user_mail1',
            'dest_user_mail2',
            'dest_user_mail3',
            'dest_user_mail4',
            'dest_user_mail5',
            'dest_user_mail6',
            'dest_user_mail7',
            'dest_user_mail8',
            'end_date',
            'auth_meth',
            'dl_limit',
            'password',
            'decode_token',
            'url',
            'message'
        )
        error_messages = {
            'end_date': {
                'required': '必須です!',
            }}

    def __init__(self, *args, **kwargs):
        # Viewからログインユーザーを取得
        self.user = kwargs.pop('user', None)
        self.url = kwargs.pop('url', None)
        super(ManageTasksUrlStep1Form, self).__init__(*args, **kwargs)

    def clean_title(self):

        # ログインユーザーと同じ会社のユーザーidを取得
        created_user = []
        users = User.objects.filter(company=self.user.company.id)
        for user in users:
           created_user.append(user.id)
        
        # formに入力された値を取得
        title = self.cleaned_data['title']
        # タイトル制限
        if self.url != "step1_url_update" :
            url_upload_manages = UrlUploadManage.objects.filter(created_user__in=created_user).all()
            for url_upload_manage in url_upload_manages:
                if url_upload_manage.tmp_flag == 0:
                    if url_upload_manage.title == title:
                        raise forms.ValidationError(
                            mark_safe('同じタイトルが既に存在しています。'))

        return title        

class UrlDistFileUploadForm(forms.ModelForm):

    class Meta:
        model = UrlUploadManage
        fields = ('file',)


"""
URL認証用のフォーム
"""


class UrlFileDownloadAuthMailForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput, required=False)

    class Meta:
        model = UrlUploadManage
        fields = ('email')


class UrlFileDownloadAuthPassForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = UrlUploadManage
        fields = ('email','password')