from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView, ListView
from draganddrop.views.home.home_common import CommonView, total_data_usage, resource_management_calculation_process
from django.contrib.auth.mixins import LoginRequiredMixin
# from ...forms import FileForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksguestStep1Form, guestDistFileUploadForm, guestFileDownloadAuthForm, ManageTasksGuestUploadCreateStep1Form
from ...forms import FileForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksGuestUploadCreateStep1Form,GuestFileUploadAuthForm,GuestUploadDistFileUploadForm
from draganddrop.models import Filemodel, PDFfilemodel, Address, Group, GuestUploadManage, GuestUploadDownloadtable, GuestUploadDownloadFiletable, ResourceManagement, PersonalResourceManagement
from accounts.models import User, Company, Messages, Service,FileupPermissions
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core import serializers
import datetime
import urllib.parse
import os
from django.conf import settings
import random
import string
import threading
from accounts.models import Notification,User
# # 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired, loads

from django.contrib.sites.shortcuts import get_current_site
from dateutil.relativedelta import relativedelta
# テンプレート情報取得
from django.template.loader import get_template
#メール送信
from django.core.mail import send_mail
# フロントへメッセージ送信
from django.contrib import messages
from django.http import JsonResponse
import json
#操作ログ関数
from lib.my_utils import add_log
#メール送信
from django.core.mail import send_mass_mail
# テンプレート情報取得
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site

Token_LENGTH = 5  # ランダムURLを作成するためのTOKEN

###########################
# ゲストアップロードレコード作成  #
###########################

class Step1GuestUploadCreate(FormView, CommonView):
    model = GuestUploadManage
    template_name = 'draganddrop/guest_upload_create/step1_guest_upload_create.html'
    form_class = ManageTasksGuestUploadCreateStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(Step1GuestUploadCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'dest_user': self.request.user.email})
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs

    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'guest_upload_manage_id' in self.request.session:
            guest_upload_manage_id = self.request.session['guest_upload_manage_id']
            guest_upload_manage = GuestUploadManage.objects.filter(pk=guest_upload_manage_id).prefetch_related('dest_user').first()

            initial = {
                'title': guest_upload_manage.title,
                'dest_user': guest_upload_manage.dest_user,
                'end_date': guest_upload_manage.end_date,
                'message': guest_upload_manage.message,
                'guest_user_mail':guest_upload_manage.guest_user_mail,
                'guest_user_name':guest_upload_manage.guest_user_name,
            }

            # 返す
            return initial



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # """ アドレス帳の情報 """
        # address_lists = Address.objects.filter(created_user=self.request.user.id, is_direct_email=False)
        # context["address_lists"] = address_lists

        # """ グループ一覧の情報 """
        # group_lists = Group.objects.filter(created_user=self.request.user.id)
        # context["group_lists"] = group_lists

        """ URL有効期限情報 """
        seven_days = datetime.datetime.now() + datetime.timedelta(days=6)
        context['seven_days'] = seven_days

        """ ユーザーメール """
        context['user_mail'] = self.request.user.email


        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'guest_upload_manage_id' in self.request.session:
            # セッションに存在するテンポラリオブジェクトモデルのIDを取得
            guest_upload_manage_id = self.request.session['guest_upload_manage_id']

            # モデルオブジェクトを取得
            guest_upload_manage = GuestUploadManage.objects.filter(pk=guest_upload_manage_id).prefetch_related('dest_user').first()

            #context["dest_users"] = upload_manage.dest_user.all()
            # アドレス帳の選択済みユーザー一覧をテンプレートへ渡す
            # pk_list = guest_upload_manage.dest_user.all().values_list('pk', flat=True)
            # context["pk_list"] = list(pk_list)

            # group_list = guest_upload_manage.dest_user_group.all().values_list('pk', flat=True)
            # context["group_list"] = list(group_list)

        return context


    def form_valid(self, form):

        user = self.request.user
        if 'guest_upload_manage_id' in self.request.session:
            # guest_upload_manage_obj = GuestUploadManage.objects.filter(pk=self.request.session['guest_upload_manage_id']).prefetch_related('dest_user').first()
            guest_upload_manage_obj = GuestUploadManage.objects.filter(pk=self.request.session['guest_upload_manage_id']).first()

        else:
            # フォームからDBのオブジェクトを仮生成（未保存）
            guest_upload_manage_obj = form.save(commit=False)

        # # ログインユーザーを登録ユーザーとしてセット
        guest_upload_manage_obj.created_user = self.request.user.id
        # # ログインユーザーの会社idをセット
        guest_upload_manage_obj.company = self.request.user.company.id
        # # 作成日をセット
        guest_upload_manage_obj.created_date = datetime.datetime.now()
        # # テンポラリフラグをセット
        guest_upload_manage_obj.tmp_flag = 1

        # # 保存期日とタイトルに関しても上記と同じように取得
        title = form.cleaned_data['title']
        message = form.cleaned_data['message']
        guest_mail = form.cleaned_data['guest_mail']
        guest_name = form.cleaned_data['guest_name']

        # それぞれをDBに代入
        guest_upload_manage_obj.title = title
        guest_upload_manage_obj.message = message
        guest_upload_manage_obj.guest_user_mail = guest_mail
        guest_upload_manage_obj.guest_user_name = guest_name

        #URL有効期限を今日の日付から7日後の23:59:59にする
        end_date = guest_upload_manage_obj.created_date + relativedelta(days=+6,hour=23,minute=59,second=59,microsecond=999999)
        guest_upload_manage_obj.end_date = end_date

        # 保存
        guest_upload_manage_obj.save()

        # メールアドレス直接入力DBへ保存
        # dest_user = form.cleaned_data['dest_user']

        # if dest_user_mail1:
        #     address1, created = Address.objects.update_or_create(
        #         email=dest_user_mail1)
        #     address1.is_direct_email = True
        #     address1.full_name_preview = dest_user_mail1
        #     address1.save()

        #URLの作成
        #ランダムな文字列を作る
        def get_random_chars(char_num=Token_LENGTH):
            return "".join([random.choice(string.ascii_letters + string.digits) for i in range(char_num)])

        # アクティベーションURL生成
        Timestamp_signer = TimestampSigner()
        context = {}
        token = get_random_chars()
        guest_upload_manage_obj.decode_token = token #tokenをDBに保存
        token_signed = Timestamp_signer.sign(token)  # ランダムURLの生成
        context["token_signed"] = token_signed
        current_site = get_current_site(self.request)
        domain = current_site.domain
        protocol = self.request.scheme
        guest_upload_manage_obj.url = protocol + "://" + domain + "/" + "guest_check" + "/" + token_signed

        # upload_manageに追加する。データを追加し、戻った際にデータを反映させるため）      
        guest_upload_manage_obj.dest_user = self.request.user.email
            
        # # POSTで送信された設定された宛先ユーザーを取得
        # dest_user_qs = form.cleaned_data['dest_user']
        # # MonyToMonyの値はquerysetとして取得するので、set関数を使ってセット
        # guest_upload_manage_obj.dest_user.set(dest_user_qs)

        # dest_user_group_qs = form.cleaned_data['dest_user_group']
        # guest_upload_manage_obj.dest_user_group.set(dest_user_group_qs)

        # if dest_user_mail1:
        #     guest_upload_manage_obj.dest_user.add(address1)
        # if dest_user_mail2:
        #     guest_upload_manage_obj.dest_user.add(address2)
        # if dest_user_mail3:
        #     guest_upload_manage_obj.dest_user.add(address3)
        # if dest_user_mail4:
        #     guest_upload_manage_obj.dest_user.add(address4)
        # if dest_user_mail5:
        #     guest_upload_manage_obj.dest_user.add(address5)
        # if dest_user_mail6:
        #     guest_upload_manage_obj.dest_user.add(address6)
        # if dest_user_mail7:
        #     guest_upload_manage_obj.dest_user.add(address7)
        # if dest_user_mail8:
        #     guest_upload_manage_obj.dest_user.add(address8)

        # # dest_userをsessionに追加するためQSをリスト化して保存。
        dest_user_all_list = []

        # for user in dest_user_qs:
        #     if user.company_name:
        #         dest_user_all_list.append(user.company_name +" " + user.last_name + "" + user.first_name + " " + "1")
        #     elif user.company_name == None:
        #         dest_user_all_list.append( user.last_name + "" + user.first_name + " " + "1")
        #     elif user.trade_name:
        #         dest_user_all_list.append(user.trade_name +" " + user.last_name + "" + user.first_name + " " + "1")
        #     else:
        #         dest_user_all_list.append(user.last_name + "" + user.first_name + " " + "1")
        
        # for group in dest_user_group_qs:
        #     dest_user_all_list.append(group.group_name + " " + "2")

        # if dest_user_mail1:
        #     dest_user_all_list.append(dest_user_mail1 + " " + "1")
        # if dest_user_mail2:
        #     dest_user_all_list.append(dest_user_mail2 + " " + "1")
        # if dest_user_mail3:
        #     dest_user_all_list.append(dest_user_mail3 + " " + "1")
        # if dest_user_mail4:
        #     dest_user_all_list.append(dest_user_mail4 + " " + "1")
        # if dest_user_mail5:
        #     dest_user_all_list.append(dest_user_mail5 + " " + "1")
        # if dest_user_mail6:
        #     dest_user_all_list.append(dest_user_mail6 + " " + "1")
        # if dest_user_mail7:
        #     dest_user_all_list.append(dest_user_mail7 + " " + "1")
        # if dest_user_mail8:
        #     dest_user_all_list.append(dest_user_mail8 + " " + "1")

        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # # POST送信された情報をセッションへ保存
        self.request.session['end_date'] = end_date
        self.request.session['dest_user_all_list'] = dest_user_all_list
        self.request.session['title'] = title
        self.request.session['message'] = message
        self.request.session['dest_user'] = guest_upload_manage_obj.dest_user
        self.request.session['guest_mail'] = guest_mail
        self.request.session['guest_name'] = guest_name


        # 保存
        guest_upload_manage_obj.save()
        guest_upload_manage_id = str(guest_upload_manage_obj.id)
        
        # 依頼先へ共有リクエストメールを送信する
        current_site = get_current_site(self.request)
        domain = current_site.domain
        end_date2 = guest_upload_manage_obj.end_date
        end_date_text = str(end_date2.year) + '年' + str(end_date2.month) + '月' +  str(end_date2.day) + '日'
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'user_last_name':self.request.user.last_name,
            'user_first_name':self.request.user.first_name,
            'guest_name':guest_name,
            'message':message,
            'end_date':end_date_text,
            'token': dumps(str(guest_upload_manage_id))
        }

        subject_template = get_template('draganddrop/guest_upload/mail_template/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('draganddrop/guest_upload/mail_template/message.txt')
        message = message_template.render(context)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [guest_mail]
        
        send_mail(subject, message, from_email, recipient_list)

        # # 生成されたDBの対象行のIDをセッションに保存しておく
        self.request.session['guest_upload_manage_id'] = guest_upload_manage_id

        # ステップ2へ遷移(作成完了画面)
        return HttpResponseRedirect(reverse('draganddrop:step2_guest_upload_create', kwargs={'pk': guest_upload_manage_id}))


class Step2GuestUploadCreate(TemplateView, CommonView):
    template_name = 'draganddrop/guest_upload_create/step2_guest_upload_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guest_upload_manage_id = self.kwargs['pk']

        context["guest_upload_manage_id"] = guest_upload_manage_id

        guest_upload_manage_obj = GuestUploadManage.objects.filter(pk=guest_upload_manage_id).first()

        guest_upload_manage_obj.tmp_flag = 0

        guest_upload_manage_obj.save()

        context["guest_upload_manage_obj"] = guest_upload_manage_obj


        # guest_upload_manageに紐付くグループを取得
        # dest_user_groups = guest_upload_manage_obj.dest_user_group.all()
        # for group in dest_user_groups:
        #     for download_user in group.address.all():
        #         # ユーザー毎のダウンロード状況を管理するテーブルを作成
        #         guest_downloadtable, created = GuestUploadDownloadtable.objects.get_or_create(guest_upload_manage=guest_upload_manage_obj, dest_user=download_user)
        #         guest_downloadtable.save()

                # GuestDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
                # for file in guest_upload_manage_obj.file.all():
                #     # ファイル毎のダウンロード状況を管理するテーブルを作成
                #     guest_downloadfiletable, created = GuestUploadDownloadFiletable.objects.get_or_create(guest_download_table=guest_downloadtable, download_file=file)
                #     guest_downloadfiletable.download_file = file
                #     guest_downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        # for download_user in guest_upload_manage_obj.dest_user.all():
        #     guest_downloadtable, created = GuestUploadDownloadtable.objects.get_or_create(guest_upload_manage=guest_upload_manage_obj, dest_user=download_user)
        #     guest_downloadtable.save()

        #     # GuestDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
        #     for file in guest_upload_manage_obj.file.all():
        #         # ファイル毎のダウンロード状況を管理するテーブルを作成
        #         guest_downloadfiletable, created = GuestUploadDownloadFiletable.objects.get_or_create(guest_download_table=guest_downloadtable, download_file=file)
        #         guest_downloadfiletable.download_file = file
        #         guest_downloadfiletable.save()
        
        
        # ファイル毎のダウンロード状況を管理するテーブルを作成
        guest_downloadtable, created = GuestUploadDownloadtable.objects.get_or_create(guest_upload_manage=guest_upload_manage_obj, dest_user=guest_upload_manage_obj.dest_user)
        guest_downloadtable.save()

        
        # ログインユーザーが作成したguest_upload_manageを取得
        personal_user_guest_upload_manages = GuestUploadManage.objects.filter(created_user=self.request.user.id).all()
        guest_upload_manage_file_size = 0
        download_table = 0
        download_file_table = 0

        for personal_user_guest_upload_manage in personal_user_guest_upload_manages:

            # ファイルの合計サイズを取得
            # for file in personal_user_guest_upload_manage.file.all():
            #     guest_upload_manage_file_size = guest_upload_manage_file_size + int(file.size)

            # guest_download_tableのレコード数を取得
            download_table += GuestUploadDownloadtable.objects.filter(guest_upload_manage=personal_user_guest_upload_manage).all().count()

            # guest_download_file_tableのレコード数を取得
            for guestdownloadtable in GuestUploadDownloadtable.objects.filter(guest_upload_manage=personal_user_guest_upload_manage).all():
                download_file_table += int(guestdownloadtable.guest_upload_download_table.all().count())

        # 個人管理テーブルの作成・更新
        total_data_usage(guest_upload_manage_obj, self.request.user.company.id, self.request.user.id, download_table, download_file_table, guest_upload_manage_file_size, 4)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)
            
        return context

##################################
# guest登録時の戻る処理 #
##################################

# class GuestUploadCreateReturnView(View):
#     def get(self, request, *args, **kwargs):

#         # 不正な遷移をチェック
#         if not 'page_num' in self.request.session:
#             raise PermissionDenied

#         page_num = self.request.session['page_num']

#         guest_upload_manage_id = self.kwargs['pk']  # 旧データ

#         # 2ページから1ページに戻る時の処理
#         if page_num == 1:
#             return HttpResponseRedirect(reverse('draganddrop:step1_guest_upload_create'))

###########################
# ゲストによるファイル共有#
###########################
#URLの認証
class GuestApproveView(TemplateView):
    model = GuestUploadManage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URLを返す
        url_name = self.request.resolver_match.url_name
        print('url_nameとは',url_name)
        context["url_name"] = url_name
        return context

    def get(self, request, token):
        if token:
            try:
                # TOKENが有効なら
                unsigned_token = loads(token)
                guest_upload_manage = GuestUploadManage.objects.get(pk=unsigned_token)
                end_date = guest_upload_manage.end_date
                current_time = datetime.datetime.now(datetime.timezone.utc)
                file_del_flag = guest_upload_manage.file_del_flag
                
                if end_date > current_time and file_del_flag==0 and guest_upload_manage.url_invalid_flag == False:
                    guest_upload_manage_id = str(guest_upload_manage.id)
                    self.request.session['guest_upload_manage_id'] = guest_upload_manage_id
                    return HttpResponseRedirect(reverse('draganddrop:guest_file_upload_auth', kwargs={'pk': guest_upload_manage.id}))
                elif end_date > current_time and file_del_flag == 1:
                    return HttpResponseRedirect(reverse('draganddrop:guest_file_unable_upload'))
                
                else:
                    return HttpResponseRedirect(reverse('draganddrop:guest_file_unable_upload'))


            except SignatureExpired:
                return render(request, self.template_name)

##################################
# ゲスト 認証画面 #
##################################
class GuestFileUploadAuth(FormView):

    model = GuestUploadManage
    template_name = 'draganddrop/guest_upload/guest_upload_auth.html'
    form_class = GuestFileUploadAuthForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URLを返す
        url_name = self.request.resolver_match.url_name
        context["url_name"] = url_name
        return context

    def form_valid(self, form):
        email = self.request.POST.get('email') #formに入力したアドレスを取得
        password = self.request.POST.get('password')  # formに入力したパスワードを取得
        self.request.session['email'] = email #次のDL画面でデータを取得するためsessionに保存
        guest_upload_manage_id = self.kwargs['pk']
        guest_upload_manage = GuestUploadManage.objects.filter(
            pk=guest_upload_manage_id).first()

        # if guest_upload_manage.dest_user_group:
        #     group_email_list = []
        #     group_lists = guest_upload_manage.dest_user_group.all()
        #     for group in group_lists:
        #         address_instances = group.address.all()
        #         for address_instance in address_instances:
        #             group_email_list.append(address_instance.email)

        now =  datetime.datetime.now(datetime.timezone.utc)
        five_min = guest_upload_manage.password_create_time + datetime.timedelta(minutes=5)
        if guest_upload_manage.guest_user_mail == email and guest_upload_manage.password == password:
            if five_min > now:
                #OTP一致でファイル表示
                self.request.session['otp_result'] = 'success' #次のDL画面への不正遷移防止のためsessionに保存
                return HttpResponseRedirect(reverse('draganddrop:step1_guest_upload', kwargs={'pk': guest_upload_manage.id}))
            else:
                messages.info(self.request, "ワンタイムパスワードの有効期限が切れています。")
                return HttpResponseRedirect(reverse('draganddrop:guest_file_upload_auth', kwargs={'pk': guest_upload_manage.id}))
        else:
            messages.info(self.request, "正しいメールアドレスまたはワンタイムパスワードを入力して下さい")
            return HttpResponseRedirect(reverse('draganddrop:guest_file_upload_auth', kwargs={'pk': guest_upload_manage.id}))

##################################
# ゲストアップロード パスワード送信Ajax #
##################################
class GuestSendAjaxView(View):
    
    def post(self, request):
        guest_upload_manage_id = self.request.session['guest_upload_manage_id']
        guest_upload_manage = GuestUploadManage.objects.filter(
            pk=guest_upload_manage_id).first()
        email = request.POST.get('email')

        if guest_upload_manage.guest_user_mail == email:
            
            #OTPを送る処理
            #パスワード生成(６桁の数字　制限時間５分)
            random_number = random.randint(100000, 999999)
            pw = random_number
            guest_upload_manage.password = pw
            guest_upload_manage.password_create_time = datetime.datetime.now()

            guest_upload_manage.save()

            # OTPの送付
            context = {
                'pw':pw,
                'email': email,
                'guest_name':guest_upload_manage.guest_user_name,
            }

            subject_template = get_template('draganddrop/guest_upload/mail_template2/subject.txt')
            subject = subject_template.render(context)

            message_template = get_template('draganddrop/guest_upload/mail_template2/message.txt')
            message = message_template.render(context)

            from_email = "cloudlab-yano@yui.okinawa"
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)
            data = {
                'messages':'指定のメールアドレスにワンタイムパスワードを送信しました。'
            }
        else:
            data = {
                'messages':'正しいメールアドレスを入力してください。'
            }
        return JsonResponse(data)

##################################
# ゲストアップロード 有効期限切れ  #
##################################

class GuestFileUnableUpload(ListView):
    model = GuestUploadManage
    template_name = 'draganddrop/guest_upload/guest_upload_auth.html'

    def index(request):
        return render(request, 'draganddrop/guest_upload/guest_upload_auth.html')

###########################
# ゲストアップロード１  #
###########################

class Step1GuestUpload(CreateView, FormView):
    model = GuestUploadManage
    template_name = "draganddrop/guest_upload/step1_guest_upload.html"
    form_class = GuestUploadDistFileUploadForm

    def dispatch(self, request, *args, **kwargs):
        # 不正遷移check
        if not 'otp_result' in self.request.session:
                return HttpResponseRedirect(reverse('draganddrop:home'))

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guest_upload_manage_id = self.kwargs['pk']
        context["guest_upload_manage_id"] = guest_upload_manage_id

        guest_upload_manage_obj = GuestUploadManage.objects.filter(pk=guest_upload_manage_id).prefetch_related('file').first()
        files = guest_upload_manage_obj.file.all()
        print('ふぁいるずの中身あるの？？？？',files) 
        context["files"] = files
        context["guest_upload_manage"] = guest_upload_manage_obj

        file = serializers.serialize("json", files, fields=('name', 'size', 'upload', 'id'))

        context["dist_file"] = file

        # 削除IDを取得
        if 'del_file_pk' in self.request.session:
            context["del_file_pk"] = self.request.session['del_file_pk']

        else:
            context["del_file_pk"] = None

        return context

    def post(self, request, *args, **kwargs):
        self.del_file = request.POST.getlist('del_file')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form,**kwargs):
        context = super().get_context_data(**kwargs)
        guest_upload_manage_id = self.kwargs['pk']
        guest_upload_manage_obj = GuestUploadManage.objects.filter(pk=guest_upload_manage_id).first()

        # ファイルの削除
        if self.del_file:
            del_file_pk = self.del_file
            self.request.session['del_file_pk'] = del_file_pk

        else:
            self.request.session['del_file_pk'] = ""

        if 'up_file_id' in self.request.session:

            # ファイルとタスクを紐付ける
            # ファイル情報をセッションから取得
            up_file_id_str = self.request.session['up_file_id'].replace(" ", "").replace("[", "").replace("]", "")

            # リストに変換
            up_file_id_list = up_file_id_str.split(',')

            # リストのInt型に変換
            up_file_id_int = [int(s) for s in up_file_id_list]

            # オブジェクトの取得
            files = Filemodel.objects.filter(pk__in=up_file_id_int)

            # タスクとファイルを紐付ける
            for file in files:

                guest_upload_manage_obj.file.add(file)

                t = threading.Thread
                # PDF変換
                # ①ファイル名から拡張子のみ取得
                file_name = file.name

                file_name_without_dot = os.path.splitext(file_name)[1][1:]
                file_name_no_extention = os.path.splitext(file_name)[0]

                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)

                # ファイルパスを分割してファイル名だけ取得
                file_name = file_path.split('/', 2)[2]

                # パスを取得
                # path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                path = os.path.join(settings.FULL_MEDIA_ROOT_FREETMP, file_name)
                print('----urlのpathはなに',path)


                # .txtファイルをHTMLファイルへ変換
                # テキストファイルを一括で読み込む
                # if file_name_without_dot == "txt":
                #     # path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                #     path = os.path.join(settings.FULL_MEDIA_ROOT_FREETMP, file_name)
                #     with open(path) as f:
                #         s = f.read()

                #         # htmlファイルを生成して書き込む
                #         upload_s = str(file.upload)
                #         upload_ss = upload_s.split('/')[0]
                #         print('upload_ssとは',upload_ss)
                #         file_path = urllib.parse.unquote(file.upload.url)

                #         upload = file_path[1:]
                #         upload_path = upload.split('.')
                #         path_html = upload_path[0] + ".html"
                #         with open(path_html, mode='w') as f:
                #             f.write("<html>\n")
                #             f.write("<head>\n")
                #             f.write("</head>\n")
                #             f.write("<body>\n")
                #             f.write("<pre>\n")
                #             f.write(s)
                #             f.write("</pre>\n")
                #             f.write("</body>\n")
                #             f.write("</html>\n")
                #         htmlfilename = path_html
                #         htmlname = os.path.basename(htmlfilename)
                #         path_html_s = upload_ss + "/" + htmlname
                        
                #         htmlfile, created = PDFfilemodel.objects.get_or_create(
                #             name=htmlname,
                #             size=file.size,
                #             upload=path_html_s,
                #             file=file,
                #         )

                #         htmlfile.save()

        guest_upload_manage_obj.save()

        return HttpResponseRedirect(reverse('draganddrop:step2_guest_upload', kwargs={'pk': guest_upload_manage_obj.id}))



class Step2GuestUpload(TemplateView):  # サーバサイドだけの処理
    template_name = 'draganddrop/guest_upload/step2_guest_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guest_upload_manage_id = self.kwargs['pk']

        guest_upload_manage = GuestUploadManage.objects.filter(pk=guest_upload_manage_id).prefetch_related('file').first()

        guest_upload_manage.uploaded_date = datetime.datetime.now()
        
        guest_upload_manage.url_invalid_flag = True
        # Downloadtableへ保存

        # グループに紐付くdownloadtableの作成
        # dest_user_groups = guest_upload_manage_tmp.dest_user_group.all()
        # for dest_user_group in dest_user_groups:
        #     for download_user in dest_user_group.address.all():
        #         guest_downloadtable, created = GuestUploadDownloadtable.objects.get_or_create(guest_upload_manage=guest_upload_manage, dest_user=download_user)
        #         guest_downloadtable.save()

        #         # Downloadfiletableへ保存
        #         for file in guest_upload_manage_file.all():
        #             guest_downloadfiletable, created = GuestUploadDownloadFiletable.objects.get_or_create(guest_download_table=guest_downloadtable, download_file = file )
        #             guest_downloadfiletable.save()


        # アドレス帳から選択したユーザーと直接入力に紐付くdownloadtableの作成
        # for download_user in guest_upload_manage_tmp.dest_user.all():
        #     guest_downloadtable, created = GuestUploadDownloadtable.objects.get_or_create(guest_upload_manage=guest_upload_manage, dest_user=download_user)
        #     guest_downloadtable.save()

        #     # Downloadfiletableへ保存
        #     for file in guest_upload_manage_file.all():
        #         guest_downloadfiletable, created = GuestUploadDownloadFiletable.objects.get_or_create(guest_download_table=guest_downloadtable, download_file=file)
        #         guest_downloadfiletable.save()

        # guest_downloadfiletables = GuestUploadDownloadFiletable.objects.filter(guest_download_table=guest_downloadtable).count()
        # guest_downloadfiletables_true = GuestUploadDownloadFiletable.objects.filter(
        #     guest_download_table=guest_downloadtable, is_downloaded=True).count()

        # if guest_downloadfiletables == guest_downloadfiletables_true:
        #     guest_downloadtable.is_downloaded = True

        # else:
        #     guest_downloadtable.is_downloaded = False
        #     guest_downloadtable.save()

        # guest_file_number = GuestUploadDownloadtable.objects.filter(
        #     guest_upload_manage=guest_downloadtable.guest_upload_manage).count()
        # guest_downloaded_file_number = GuestUploadDownloadtable.objects.filter(
        #     guest_upload_manage=guest_downloadtable.guest_upload_manage, is_downloaded=True).count()

        # if guest_file_number == guest_downloaded_file_number:
        #     guest_downloadtable.guest_upload_manage.is_downloaded = True  # 対応完了

        # else:
        #     guest_upload_manage = guest_downloadtable.guest_upload_manage
        #     guest_upload_manage.is_downloaded = False
        #     guest_upload_manage.save()

        # guest_downloadtable.save()

        # for file in guest_upload_manage_tmp.file.all():
        #     guest_upload_manage.file.add(file)

        guest_upload_manage.save()

        #操作ログ用
        #送信元（ゲスト）
        current_user = self.request.user
        guest_mail = guest_upload_manage.guest_user_mail
        guest_name = guest_upload_manage.guest_user_name
        guest = guest_mail + '/' + guest_name
        #送信先(自分)
        dest_users = current_user.email
        # ファイル名
        guestupload_files = guest_upload_manage.file.all()
        print('ふぁいるかくにん00000ここはきてる？？',guestupload_files)           
        files = []
        for file in guestupload_files:
            print('ふぁいるかくにん00000',file.name)           
            file_name = file.name + "\r\n"
            files.append(file_name)
        files = ' '.join(files)
        # ファイルタイトル
        file_title = guest_upload_manage.title
        # 操作ログ終わり
        # 操作ログ
        add_log(2,1,guest,file_title,files,dest_users,6,self.request.META.get('REMOTE_ADDR'))
        ###################　Notification通知用  ～を受信しました 操作ログの下にいれる
        #送信先 (自分)email
        emailList_db = current_user.email
        #タイトル
        Notice_title = guest + "さんが" + file_title + "を共有しました。"
        #メッセージ
        Notice_message = guest_upload_manage.message

        ###通知テーブル登録
        Notification.objects.create(service="FileUP!",category="受信通知",sender=guest,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

        #メール送信
        current_site = get_current_site(self.request)
        domain = current_site.domain

        print('いーめーるげすと',emailList_db)
        e_user = User.objects.get(email=emailList_db)
        # tupleMessage = []
        # for user_email in emailList_db:
        #     e_user = User.objects.get(email=user_email)
        #     print('いーめーるげすとkorewakaru?',e_user)
        e_send = e_user.is_send_mail
        print('めーーーる可否',e_send)

        if e_send == True:
            context = {
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': domain,
                #送信者(この場合ゲストユーザー)
                'user_last_name':guest_name,
                # 'user_first_name':self.request.user.first_name,
            }
            subject_template = get_template('draganddrop/mail_template/subject.txt')
            subject = subject_template.render(context)

            message_template = get_template('draganddrop/mail_template/message.txt')
            message = message_template.render(context)
            from_email = settings.EMAIL_HOST_USER#CL側のメアド
            recipient_list = [emailList_db]#受信者リスト
            
            # message1 = (
            #     subject,
            #     message,
            #     from_email,
            #     recipient_list,
            # )
            # messageList = list(message1)
            # tupleMessage.insert(-1,messageList)
            send_mail(subject, message, from_email, recipient_list)
        # send_mass_mail(tupleMessage)
        ##################Notification通知用終了

        personal_resource_manage = PersonalResourceManagement.objects.filter(user=guest_upload_manage.created_user).first()

        # ファイルの合計サイズ
        guest_upload_manage_file_size = 0
        for file in guest_upload_manage.file.all():
            guest_upload_manage_file_size = guest_upload_manage_file_size + int(file.size)
        personal_resource_manage.guest_upload_manage_file_size += guest_upload_manage_file_size

        # guest_upload_download_file_tableのレコード数を更新
        number_of_guest_upload_download_file_table = 0
        for guestuploaddownloadtable in GuestUploadDownloadtable.objects.filter(guest_upload_manage=guest_upload_manage).all():
            number_of_guest_upload_download_file_table += int(guestuploaddownloadtable.guest_upload_download_table.all().count())
        personal_resource_manage.number_of_guest_upload_download_file_table += number_of_guest_upload_download_file_table

        personal_resource_manage.save()

        # tmpレコード削除 (allになっているのが気になる)
        guest_tmp_flag_1 = GuestUploadManage.objects.filter(tmp_flag=1).all()
        guest_tmp_flag_1.delete()

        download_table = personal_resource_manage.number_of_guest_upload_download_table
        download_file_table = personal_resource_manage.number_of_guest_upload_download_file_table
        total_file_size = personal_resource_manage.total_file_size
        user = User.objects.filter(email=guest_upload_manage.dest_user).first()
        
        # 個人管理テーブルの作成・更新
        total_data_usage(guest_upload_manage, user.company.id, user.id, download_table, download_file_table, guest_upload_manage_file_size, 4)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(user.company.id)
        # this_personal_resource_manage.save()

        return context

# ##################################
# # Guestファイルアップロード変更時の戻る処理  #
# ##################################

# class GuestReturnUpdateView(View):
#     def get(self, request, *args, **kwargs):

#         # 不正な遷移をチェック
#         if not 'page_num' in self.request.session:
#             raise PermissionDenied

#         page_num = self.request.session['page_num']

#         guest_upload_manage_id_old = self.kwargs['pk']  # 旧データ

#         # 2ページから1ページに戻る時の処理
#         if page_num == 1:
#             return HttpResponseRedirect(reverse('draganddrop:step1_guest_update', kwargs={'pk': guest_upload_manage_id_old}))