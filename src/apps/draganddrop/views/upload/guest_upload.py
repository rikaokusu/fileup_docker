from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView
from draganddrop.views.home.home_common import CommonView, total_data_usage, resource_management_calculation_process
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import FileForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksOTPStep1Form, OTPDistFileUploadForm, OTPFileDownloadAuthForm, ManageTasksGuestUploadCreateStep1Form
from draganddrop.models import Filemodel, PDFfilemodel, Address, Group, OTPUploadManage, OTPDownloadtable, OTPDownloadFiletable, GuestUploadManage, GuestUploadDownloadtable, GuestUploadDownloadFiletable, ResourceManagement, PersonalResourceManagement
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
# # 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired
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
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs

    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'otp_upload_manage_id' in self.request.session:
            otp_upload_manage_id = self.request.session['otp_upload_manage_id']
            otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user').first()

            initial = {
                'title': otp_upload_manage.title,
                'dest_user': otp_upload_manage.dest_user.all(),
                'dest_user_group': otp_upload_manage.dest_user_group.all(),
                'dest_user_mail1': otp_upload_manage.dest_user_mail1,
                'dest_user_mail2': otp_upload_manage.dest_user_mail2,
                'dest_user_mail3': otp_upload_manage.dest_user_mail3,
                'dest_user_mail4': otp_upload_manage.dest_user_mail4,
                'dest_user_mail5': otp_upload_manage.dest_user_mail5,
                'dest_user_mail6': otp_upload_manage.dest_user_mail6,
                'dest_user_mail7': otp_upload_manage.dest_user_mail7,
                'dest_user_mail8': otp_upload_manage.dest_user_mail8,
                'end_date': otp_upload_manage.end_date,
                'message': otp_upload_manage.message,
            }

            # 返す
            return initial


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """ アドレス帳の情報"""
        address_lists = Address.objects.filter(created_user=self.request.user.id, is_direct_email=False)
        context["address_lists"] = address_lists

        """ グループ一覧の情報"""
        group_lists = Group.objects.filter(created_user=self.request.user.id)
        context["group_lists"] = group_lists
        
        """ URL有効期限情報 """
        seven_days = datetime.datetime.now() + datetime.timedelta(days=6)
        context['seven_days'] = seven_days
        

        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'otp_upload_manage_id' in self.request.session:
            # セッションに存在するテンポラリオブジェクトモデルのIDを取得
            otp_upload_manage_id = self.request.session['otp_upload_manage_id']

            # モデルオブジェクトを取得
            otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user').first()

            #context["dest_users"] = upload_manage.dest_user.all()
            # アドレス帳の選択済みユーザー一覧をテンプレートへ渡す
            pk_list = otp_upload_manage.dest_user.all().values_list('pk', flat=True)
            context["pk_list"] = list(pk_list)

            group_list = otp_upload_manage.dest_user_group.all().values_list('pk', flat=True)
            context["group_list"] = list(group_list)

        return context


    def form_valid(self, form):

        if 'otp_upload_manage_id' in self.request.session:
            otp_upload_manage_obj = OTPUploadManage.objects.filter(pk=self.request.session['otp_upload_manage_id']).prefetch_related('dest_user').first()

        else:
            # フォームからDBのオブジェクトを仮生成（未保存）
            otp_upload_manage_obj = form.save(commit=False)

        # # ログインユーザーを登録ユーザーとしてセット
        otp_upload_manage_obj.created_user = self.request.user.id
        # # ログインユーザーの会社idをセット
        otp_upload_manage_obj.company = self.request.user.company.id
        # # 作成日をセット
        otp_upload_manage_obj.created_date = datetime.datetime.now()
        # # テンポラリフラグをセット
        otp_upload_manage_obj.tmp_flag = 1

        # # 保存期日とタイトルに関しても上記と同じように取得
        title = form.cleaned_data['title']
        end_date = form.cleaned_data['end_date']
        message = form.cleaned_data['message']


        # それぞれをDBに代入
        otp_upload_manage_obj.end_date = end_date
        otp_upload_manage_obj.title = title
        otp_upload_manage_obj.message = message

        # 保存
        otp_upload_manage_obj.save()

        # メールアドレス直接入力DBへ保存
        dest_user_mail1 = form.cleaned_data['dest_user_mail1']

        if dest_user_mail1:
            address1, created = Address.objects.update_or_create(
                email=dest_user_mail1)
            address1.is_direct_email = True
            address1.full_name_preview = dest_user_mail1
            address1.save()

        dest_user_mail2 = form.cleaned_data['dest_user_mail2']

        if dest_user_mail2:
            address2, created = Address.objects.update_or_create(
                email=dest_user_mail2)
            address2.is_direct_email = True
            address2.full_name_preview = dest_user_mail2
            address2.save()

        dest_user_mail3 = form.cleaned_data['dest_user_mail3']

        if dest_user_mail3:
            address3, created = Address.objects.update_or_create(
                email=dest_user_mail3)
            address3.is_direct_email = True
            address3.full_name_preview = dest_user_mail3
            address3.save()

        dest_user_mail4 = form.cleaned_data['dest_user_mail4']

        if dest_user_mail4:
            address4, created = Address.objects.update_or_create(
                email=dest_user_mail4)
            address4.is_direct_email = True
            address4.full_name_preview = dest_user_mail4
            address4.save()

        dest_user_mail5 = form.cleaned_data['dest_user_mail5']

        if dest_user_mail5:
            address5, created = Address.objects.update_or_create(
                email=dest_user_mail5)
            address5.is_direct_email = True
            address5.full_name_preview = dest_user_mail5
            address5.save()

        dest_user_mail6 = form.cleaned_data['dest_user_mail6']

        if dest_user_mail6:
            address6, created = Address.objects.update_or_create(
                email=dest_user_mail6)
            address6.is_direct_email = True
            address6.full_name_preview = dest_user_mail6
            address6.save()

        dest_user_mail7 = form.cleaned_data['dest_user_mail7']

        if dest_user_mail7:
            address7, created = Address.objects.update_or_create(
                email=dest_user_mail7)
            address7.is_direct_email = True
            address7.full_name_preview = dest_user_mail7
            address7.save()

        dest_user_mail8 = form.cleaned_data['dest_user_mail8']

        if dest_user_mail8:
            address8, created = Address.objects.update_or_create(
                email=dest_user_mail8)
            address8.is_direct_email = True
            address8.full_name_preview = dest_user_mail8
            address8.save()

        #URLの作成
        #ランダムな文字列を作る
        def get_random_chars(char_num=Token_LENGTH):
            return "".join([random.choice(string.ascii_letters + string.digits) for i in range(char_num)])

        # アクティベーションURL生成
        Timestamp_signer = TimestampSigner()
        context = {}
        token = get_random_chars()
        otp_upload_manage_obj.decode_token = token #tokenをDBに保存
        token_signed = Timestamp_signer.sign(token)  # ランダムURLの生成
        context["token_signed"] = token_signed
        current_site = get_current_site(self.request)
        domain = current_site.domain
        print('domainとは',domain)
        protocol = self.request.scheme
        otp_upload_manage_obj.url = protocol + "://" + domain + "/" + "otp_check" + "/" + token_signed

        # upload_manageに追加する。データを追加し、戻った際にデータを反映させるため）
        otp_upload_manage_obj.dest_user_mail1 = dest_user_mail1
        otp_upload_manage_obj.dest_user_mail2 = dest_user_mail2
        otp_upload_manage_obj.dest_user_mail3 = dest_user_mail3
        otp_upload_manage_obj.dest_user_mail4 = dest_user_mail4
        otp_upload_manage_obj.dest_user_mail5 = dest_user_mail5
        otp_upload_manage_obj.dest_user_mail6 = dest_user_mail6
        otp_upload_manage_obj.dest_user_mail7 = dest_user_mail7
        otp_upload_manage_obj.dest_user_mail8 = dest_user_mail8

        # # POSTで送信された設定された宛先ユーザーを取得
        dest_user_qs = form.cleaned_data['dest_user']
        # # MonyToMonyの値はquerysetとして取得するので、set関数を使ってセット
        otp_upload_manage_obj.dest_user.set(dest_user_qs)

        dest_user_group_qs = form.cleaned_data['dest_user_group']
        otp_upload_manage_obj.dest_user_group.set(dest_user_group_qs)

        if dest_user_mail1:
            otp_upload_manage_obj.dest_user.add(address1)
        if dest_user_mail2:
            otp_upload_manage_obj.dest_user.add(address2)
        if dest_user_mail3:
            otp_upload_manage_obj.dest_user.add(address3)
        if dest_user_mail4:
            otp_upload_manage_obj.dest_user.add(address4)
        if dest_user_mail5:
            otp_upload_manage_obj.dest_user.add(address5)
        if dest_user_mail6:
            otp_upload_manage_obj.dest_user.add(address6)
        if dest_user_mail7:
            otp_upload_manage_obj.dest_user.add(address7)
        if dest_user_mail8:
            otp_upload_manage_obj.dest_user.add(address8)

        # # dest_userをsessionに追加するためQSをリスト化して保存。
        dest_user_all_list = []

        for user in dest_user_qs:
            if user.company_name:
                dest_user_all_list.append(user.company_name +" " + user.last_name + "" + user.first_name + " " + "1")
            elif user.company_name == None:
                dest_user_all_list.append( user.last_name + "" + user.first_name + " " + "1")
            elif user.trade_name:
                dest_user_all_list.append(user.trade_name +" " + user.last_name + "" + user.first_name + " " + "1")
            else:
                dest_user_all_list.append(user.last_name + "" + user.first_name + " " + "1")
        
        for group in dest_user_group_qs:
            dest_user_all_list.append(group.group_name + " " + "2")

        if dest_user_mail1:
            dest_user_all_list.append(dest_user_mail1 + " " + "1")
        if dest_user_mail2:
            dest_user_all_list.append(dest_user_mail2 + " " + "1")
        if dest_user_mail3:
            dest_user_all_list.append(dest_user_mail3 + " " + "1")
        if dest_user_mail4:
            dest_user_all_list.append(dest_user_mail4 + " " + "1")
        if dest_user_mail5:
            dest_user_all_list.append(dest_user_mail5 + " " + "1")
        if dest_user_mail6:
            dest_user_all_list.append(dest_user_mail6 + " " + "1")
        if dest_user_mail7:
            dest_user_all_list.append(dest_user_mail7 + " " + "1")
        if dest_user_mail8:
            dest_user_all_list.append(dest_user_mail8 + " " + "1")

        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        # # POST送信された情報をセッションへ保存
        self.request.session['end_date'] = end_date
        self.request.session['dest_user_all_list'] = dest_user_all_list
        self.request.session['title'] = title
        self.request.session['message'] = message
        self.request.session['dest_user_mail1'] = dest_user_mail1
        self.request.session['dest_user_mail2'] = dest_user_mail2
        self.request.session['dest_user_mail3'] = dest_user_mail3
        self.request.session['dest_user_mail4'] = dest_user_mail4
        self.request.session['dest_user_mail5'] = dest_user_mail5
        self.request.session['dest_user_mail6'] = dest_user_mail6
        self.request.session['dest_user_mail7'] = dest_user_mail7
        self.request.session['dest_user_mail8'] = dest_user_mail8


        # 保存
        otp_upload_manage_obj.save()
        otp_upload_manage_id = str(otp_upload_manage_obj.id)

        # # 生成されたDBの対象行のIDをセッションに保存しておく
        self.request.session['otp_upload_manage_id'] = otp_upload_manage_id

        # ステップ2へ遷移(ファイルを選択するステップ)
        return HttpResponseRedirect(reverse('draganddrop:step2_guest_upload_create', kwargs={'pk': otp_upload_manage_id}))

# class Step1GuestUploadCreate(LoginRequiredMixin, CreateView, CommonView):
#     model = OTPUploadManage
#     template_name = "draganddrop/guest_upload_create/step2_guest_upload_create.html"
#     form_class = OTPDistFileUploadForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         otp_upload_manage_id = self.kwargs['pk']
#         context["otp_upload_manage_id"] = otp_upload_manage_id

#         otp_upload_manage_obj = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('file').first()
#         files = otp_upload_manage_obj.file.all()
#         context["files"] = files

#         file = serializers.serialize("json", files, fields=('name', 'size', 'upload', 'id'))

#         context["dist_file"] = file

#         # 削除IDを取得
#         if 'del_file_pk' in self.request.session:
#             context["del_file_pk"] = self.request.session['del_file_pk']

#         else:
#             context["del_file_pk"] = None

#         return context

#     def post(self, request, *args, **kwargs):
#         self.del_file = request.POST.getlist('del_file')
#         return super().post(request, *args, **kwargs)

#     def form_valid(self, form):

#         otp_upload_manage_id = self.kwargs['pk']
#         otp_upload_manage_obj = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).first()

#         # ファイルの削除
#         if self.del_file:
#             del_file_pk = self.del_file
#             self.request.session['del_file_pk'] = del_file_pk

#         else:
#             self.request.session['del_file_pk'] = ""

#         if 'up_file_id' in self.request.session:

#             # ファイルとタスクを紐付ける
#             # ファイル情報をセッションから取得
#             up_file_id_str = self.request.session['up_file_id'].replace(" ", "").replace("[", "").replace("]", "")

#             # リストに変換
#             up_file_id_list = up_file_id_str.split(',')

#             # リストのInt型に変換
#             up_file_id_int = [int(s) for s in up_file_id_list]

#             # オブジェクトの取得
#             files = Filemodel.objects.filter(pk__in=up_file_id_int)

#             # タスクとファイルを紐付ける
#             for file in files:

#                 otp_upload_manage_obj.file.add(file)

#                 t = threading.Thread
#                 # PDF変換
#                 # ①ファイル名から拡張子のみ取得
#                 file_name = file.name

#                 file_name_without_dot = os.path.splitext(file_name)[1][1:]
#                 file_name_no_extention = os.path.splitext(file_name)[0]

#                 # 実ファイル名を文字列にデコード
#                 file_path = urllib.parse.unquote(file.upload.url)

#                 # ファイルパスを分割してファイル名だけ取得
#                 file_name = file_path.split('/', 2)[2]
#                 # file_name = file_path.split('/', 3)[3]
#                 print('----urlのfile_nameはなに',file_name)


#                 # パスを取得
#                 # path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
#                 path = os.path.join(settings.FULL_MEDIA_ROOT_FREETMP, file_name)
#                 print('----urlのpathはなに',path)


#                 # .txtファイルをHTMLファイルへ変換
#                 # テキストファイルを一括で読み込む
#                 if file_name_without_dot == "txt":
#                     # path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
#                     path = os.path.join(settings.FULL_MEDIA_ROOT_FREETMP, file_name)
#                     print('txtふぁいるにすすんだ',path)
#                     with open(path) as f:
#                         s = f.read()

#                         # htmlファイルを生成して書き込む
#                         upload_s = str(file.upload)
#                         upload_ss = upload_s.split('/')[0]
#                         print('upload_ssとは',upload_ss)
#                         file_path = urllib.parse.unquote(file.upload.url)

#                         upload = file_path[1:]
#                         upload_path = upload.split('.')
#                         path_html = upload_path[0] + ".html"
#                         with open(path_html, mode='w') as f:
#                             f.write("<html>\n")
#                             f.write("<head>\n")
#                             f.write("</head>\n")
#                             f.write("<body>\n")
#                             f.write("<pre>\n")
#                             f.write(s)
#                             f.write("</pre>\n")
#                             f.write("</body>\n")
#                             f.write("</html>\n")
#                         htmlfilename = path_html
#                         htmlname = os.path.basename(htmlfilename)
#                         path_html_s = upload_ss + "/" + htmlname
                        
#                         htmlfile, created = PDFfilemodel.objects.get_or_create(
#                             name=htmlname,
#                             size=file.size,
#                             upload=path_html_s,
#                             file=file,
#                         )

#                         htmlfile.save()

#         otp_upload_manage_obj.save()

#         return HttpResponseRedirect(reverse('draganddrop:step2_otp_upload', kwargs={'pk': otp_upload_manage_obj.id}))

class Step2GuestUploadCreate(TemplateView, CommonView):
    template_name = 'draganddrop/guest_update_create/step2_guest_upload_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        otp_upload_manage_id = self.kwargs['pk']

        context["otp_upload_manage_id"] = otp_upload_manage_id

        otp_upload_manage_obj = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).first()

        otp_upload_manage_obj.tmp_flag = 0

        otp_upload_manage_obj.save()

        context["otp_upload_manage_obj"] = otp_upload_manage_obj

        # otp_upload_manageに紐付くグループを取得
        dest_user_groups = otp_upload_manage_obj.dest_user_group.all()
        for group in dest_user_groups:
            for download_user in group.address.all():
                # ユーザー毎のダウンロード状況を管理するテーブルを作成
                otp_downloadtable, created = OTPDownloadtable.objects.get_or_create(otp_upload_manage=otp_upload_manage_obj, dest_user=download_user)
                otp_downloadtable.save()
            
                # OTPDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
                for file in otp_upload_manage_obj.file.all():
                    # ファイル毎のダウンロード状況を管理するテーブルを作成
                    otp_downloadfiletable, created = OTPDownloadFiletable.objects.get_or_create(otp_download_table=otp_downloadtable, download_file=file)
                    otp_downloadfiletable.download_file = file
                    otp_downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        for download_user in otp_upload_manage_obj.dest_user.all():
            otp_downloadtable, created = OTPDownloadtable.objects.get_or_create(otp_upload_manage=otp_upload_manage_obj, dest_user=download_user)
            otp_downloadtable.save()

            # OTPDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
            for file in otp_upload_manage_obj.file.all():
                # ファイル毎のダウンロード状況を管理するテーブルを作成
                otp_downloadfiletable, created = OTPDownloadFiletable.objects.get_or_create(otp_download_table=otp_downloadtable, download_file=file)
                otp_downloadfiletable.download_file = file
                otp_downloadfiletable.save()

        # PersonalResourceManagementへ保存
        
        # ログインユーザーが作成したotp_upload_manageを取得
        personal_user_otp_upload_manages = OTPUploadManage.objects.filter(created_user=self.request.user.id).all()
        otp_upload_manage_file_size = 0
        download_table = 0
        download_file_table = 0

        for personal_user_otp_upload_manage in personal_user_otp_upload_manages:

            # ファイルの合計サイズを取得
            for file in personal_user_otp_upload_manage.file.all():
                otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)

            # otp_download_tableのレコード数を取得
            download_table += OTPDownloadtable.objects.filter(otp_upload_manage=personal_user_otp_upload_manage).all().count()

            # otp_download_file_tableのレコード数を取得
            for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=personal_user_otp_upload_manage).all():
                download_file_table += int(otpdownloadtable.otp_download_table.all().count())

        # 個人管理テーブルの作成・更新
        total_data_usage(otp_upload_manage_obj, self.request.user.company.id, self.request.user.id, download_table, download_file_table, otp_upload_manage_file_size, 3)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)
            
        return context

##################################
# OTP登録時の戻る処理 #
##################################

class GuestUploadReturnView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        otp_upload_manage_id = self.kwargs['pk']  # 旧データ

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:step1_otp_upload'))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:step2_otp_upload', kwargs={'pk': otp_upload_manage_id}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:step3_otp_upload', kwargs={'pk': otp_upload_manage_id}))



###########################
# OTP アップデート   #
###########################

class Step1OTPUpdate(FormView, CommonView):
    model = OTPUploadManage
    template_name = 'draganddrop/otp/step1_otp_upload.html'
    form_class = ManageTasksOTPStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(Step1OTPUpdate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs

    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        otp_upload_manage_id = self.kwargs['pk']
        if 'otp_upload_manage_id' in self.request.session:
            otp_upload_manage = OTPUploadManage.objects.filter(pk=self.request.session['otp_upload_manage_id']).first()  # 新データ

            dest_user_mail1 = otp_upload_manage.dest_user_mail1
            dest_user_mail2 = otp_upload_manage.dest_user_mail2
            dest_user_mail3 = otp_upload_manage.dest_user_mail3
            dest_user_mail4 = otp_upload_manage.dest_user_mail4
            dest_user_mail5 = otp_upload_manage.dest_user_mail5
            dest_user_mail6 = otp_upload_manage.dest_user_mail6
            dest_user_mail7 = otp_upload_manage.dest_user_mail7
            dest_user_mail8 = otp_upload_manage.dest_user_mail8
            dest_user = otp_upload_manage.dest_user
            dest_user_group = otp_upload_manage.dest_user_group
            title = otp_upload_manage.title
            end_date = otp_upload_manage.end_date
            message = otp_upload_manage.message

            if otp_upload_manage.dest_user.all().count() == 0:
                otp_upload_manage_old = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
                dest_user = otp_upload_manage_old.dest_user.all()
            else:
                dest_user = otp_upload_manage.dest_user.all()

            if otp_upload_manage.dest_user_group.all().count() == 0:
                otp_upload_manage_old = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user_group',).first()  # 旧データ
                dest_user_group = otp_upload_manage_old.dest_user_group.all()
            else:
                dest_user_group = otp_upload_manage.dest_user_group.all()

            if otp_upload_manage.end_date == None:
                otp_upload_manage_old = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).first()  # 旧データ
                end_date = otp_upload_manage_old.end_date
            else:
                end_date = otp_upload_manage.end_date

            if otp_upload_manage.dl_limit == None:
                otp_upload_manage_old = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).first()  # 旧データ
                dl_limit = otp_upload_manage_old.dl_limit
            else:
                dl_limit = otp_upload_manage.dl_limit

            initial = {
                        'title': title,
                        'dest_user': dest_user,
                        'dest_user_group': dest_user_group,
                        'dest_user_mail1': dest_user_mail1,
                        'dest_user_mail2': dest_user_mail2,
                        'dest_user_mail3': dest_user_mail3,
                        'dest_user_mail4': dest_user_mail4,
                        'dest_user_mail5': dest_user_mail5,
                        'dest_user_mail6': dest_user_mail6,
                        'dest_user_mail7': dest_user_mail7,
                        'dest_user_mail8': dest_user_mail8,
                        'end_date': end_date,
                        'message': message
                    }

        # formに新たな値が書き込まれなかった時に元の旧データを返す処理。
        else:
            otp_upload_manage_old = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
            initial = {
                        'title': otp_upload_manage_old.title,
                        'dest_user': otp_upload_manage_old.dest_user.all(),
                        'dest_user_group': otp_upload_manage_old.dest_user_group.all(),
                        'dest_user_mail1': otp_upload_manage_old.dest_user_mail1,
                        'dest_user_mail2': otp_upload_manage_old.dest_user_mail2,
                        'dest_user_mail3': otp_upload_manage_old.dest_user_mail3,
                        'dest_user_mail4': otp_upload_manage_old.dest_user_mail4,
                        'dest_user_mail5': otp_upload_manage_old.dest_user_mail5,
                        'dest_user_mail6': otp_upload_manage_old.dest_user_mail6,
                        'dest_user_mail7': otp_upload_manage_old.dest_user_mail7,
                        'dest_user_mail8': otp_upload_manage_old.dest_user_mail8,
                        'end_date': otp_upload_manage_old.end_date,
                        'message': otp_upload_manage_old.message,
                        }

        # 返す
        return initial

    # アドレス帳のデータをもってくる。
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        """ アドレス帳の情報"""
        address_lists = Address.objects.filter(created_user=self.request.user.id, is_direct_email=False)
        context["address_lists"] = address_lists

        """ グループ一覧の情報"""
        group_lists = Group.objects.filter(created_user=self.request.user.id)
        context["group_lists"] = group_lists


        otp_upload_manage_id = self.kwargs['pk']
        if 'otp_upload_manage_id' in self.request.session:
            otp_upload_manage = OTPUploadManage.objects.filter(pk=self.request.session['otp_upload_manage_id']).first()  # 新データ
        else:
            otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user').first()
        
        context["dest_users"] = otp_upload_manage.dest_user.all()

        dest_user_qs = otp_upload_manage.dest_user.all().order_by('pk')
        full_name_list = []
        for dest_user in dest_user_qs:
            full_name = dest_user.last_name + " " + dest_user.first_name
            full_name_list.append(full_name)
        context["name"] = full_name_list

        company_name = dest_user_qs.values_list('company_name', flat=True)
        context["company_name"] = list(company_name)

        pk_list = dest_user_qs.values_list('pk', flat=True)
        context["pk_list"] = list(pk_list)

        dest_user_group_qs = otp_upload_manage.dest_user_group.all().order_by('pk')
        group_list = dest_user_group_qs.values_list('pk', flat=True)
        context["group_list"] = list(group_list)

        return context

    def form_valid(self, form):

        if 'otp_upload_manage_id' in self.request.session:
            otp_upload_manage = OTPUploadManage.objects.filter(pk=self.request.session['otp_upload_manage_id']).first()

        else:
            # セッションに値がない場合新たにカラムを作成する。
            otp_upload_manage = form.save(commit=False)

        title = form.cleaned_data['title']
        end_date = form.cleaned_data['end_date']
        message = form.cleaned_data['message']
        dest_user_qs = form.cleaned_data['dest_user']
        dest_user_group_qs = form.cleaned_data['dest_user_group']


        # ログインユーザーを登録ユーザーとしてセット
        otp_upload_manage.created_user = self.request.user.id
        # ログインユーザーの会社idをセット
        otp_upload_manage.company = self.request.user.company.id
        # 作成日をセット
        otp_upload_manage.created_date = datetime.datetime.now()
        # テンポラリフラグをセット
        otp_upload_manage.tmp_flag = 1
        # タイトルをセット
        otp_upload_manage.title = title
        # 終了日をセット
        otp_upload_manage.end_date = end_date
        # メッセージをセット
        otp_upload_manage.message = message


        # メールアドレス直接入力 DBへ保存
        dest_user_mail1 = form.cleaned_data['dest_user_mail1']
        

        if dest_user_mail1:
            address1, created = Address.objects.update_or_create(email=dest_user_mail1)
            address1.is_direct_email = True
            address1.full_name_preview = dest_user_mail1
            address1.save()
        
        dest_user_mail2 = form.cleaned_data['dest_user_mail2']

        if dest_user_mail2:
            address2, created = Address.objects.update_or_create(email=dest_user_mail2)
            address2.is_direct_email = True
            address2.full_name_preview = dest_user_mail2
            address2.save()
            
        dest_user_mail3 = form.cleaned_data['dest_user_mail3']

        if dest_user_mail3:
            address3, created = Address.objects.update_or_create(email=dest_user_mail3)
            address3.is_direct_email = True
            address3.full_name_preview = dest_user_mail3
            address3.save()

        dest_user_mail4 = form.cleaned_data['dest_user_mail4']

        if dest_user_mail4:
            address4, created = Address.objects.update_or_create(email=dest_user_mail4)
            address4.is_direct_email = True
            address4.full_name_preview = dest_user_mail4
            address4.save()

        dest_user_mail5 = form.cleaned_data['dest_user_mail5']

        if dest_user_mail5:
            address5, created = Address.objects.update_or_create(email=dest_user_mail5)
            address5.is_direct_email = True
            address5.full_name_preview = dest_user_mail5
            address5.save()

        dest_user_mail6 = form.cleaned_data['dest_user_mail6']

        if dest_user_mail6:
            address6, created = Address.objects.update_or_create(email=dest_user_mail6)
            address6.is_direct_email = True
            address6.full_name_preview = dest_user_mail6
            address6.save()

        dest_user_mail7 = form.cleaned_data['dest_user_mail7']

        if dest_user_mail7:
            address7, created = Address.objects.update_or_create(email=dest_user_mail7)
            address7.is_direct_email = True
            address7.full_name_preview = dest_user_mail7
            address7.save()

        dest_user_mail8 = form.cleaned_data['dest_user_mail8']

        if dest_user_mail8:
            address8, created = Address.objects.update_or_create(email=dest_user_mail8)
            address8.is_direct_email = True
            address8.full_name_preview = dest_user_mail8
            address8.save()

        # upload_manageに追加する。（データを追加し、戻った際にデータを反映させるため）
        otp_upload_manage.dest_user_mail1 = dest_user_mail1
        otp_upload_manage.dest_user_mail2 = dest_user_mail2
        otp_upload_manage.dest_user_mail3 = dest_user_mail3
        otp_upload_manage.dest_user_mail4 = dest_user_mail4
        otp_upload_manage.dest_user_mail5 = dest_user_mail5
        otp_upload_manage.dest_user_mail6 = dest_user_mail6
        otp_upload_manage.dest_user_mail7 = dest_user_mail7
        otp_upload_manage.dest_user_mail8 = dest_user_mail8

        # dest_userをsessionに追加するためQSをリスト化して保存。
        dest_user_all_list = []

        for user in dest_user_qs:
            if user.company_name:
                dest_user_all_list.append(user.company_name +" " + user.last_name + "" + user.first_name + " " + "1")
            elif user.trade_name:
                dest_user_all_list.append(user.trade_name +" " + user.last_name + "" + user.first_name + " " + "1")
            else:
                dest_user_all_list.append(user.last_name + "" + user.first_name + " " + "1")
        
        for group in dest_user_group_qs:
            dest_user_all_list.append(group.group_name + " " + "2")

        if dest_user_mail1:
            dest_user_all_list.append(dest_user_mail1 + " " + "1")
        if dest_user_mail2:
            dest_user_all_list.append(dest_user_mail2 + " " + "1")
        if dest_user_mail3:
            dest_user_all_list.append(dest_user_mail3 + " " + "1")
        if dest_user_mail4:
            dest_user_all_list.append(dest_user_mail4 + " " + "1")
        if dest_user_mail5:
            dest_user_all_list.append(dest_user_mail5 + " " + "1")
        if dest_user_mail6:
            dest_user_all_list.append(dest_user_mail6 + " " + "1")
        if dest_user_mail7:
            dest_user_all_list.append(dest_user_mail7 + " " + "1")
        if dest_user_mail8:
            dest_user_all_list.append(dest_user_mail8 + " " + "1")

        # 日付をString化
        # dist_start_date = dist_start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        # POST送信された情報をセッションへ保存
        self.request.session['title'] = title
        self.request.session['end_date'] = end_date
        self.request.session['message'] = message
        self.request.session['dest_user_all_list'] = dest_user_all_list

        otp_upload_manage.save()
        otp_upload_manage_id = str(otp_upload_manage.id)


        # # MonyToMonyの値はquerysetとして取得するのでupload_manageに保存したうえで、set関数を使ってセット
        otp_upload_manage.dest_user.set(dest_user_qs)
        otp_upload_manage.dest_user_group.set(dest_user_group_qs)

        if dest_user_mail1:
            otp_upload_manage.dest_user.add(address1)
        if dest_user_mail2:
            otp_upload_manage.dest_user.add(address2)
        if dest_user_mail3:
            otp_upload_manage.dest_user.add(address3)
        if dest_user_mail4:
            otp_upload_manage.dest_user.add(address4)
        if dest_user_mail5:
            otp_upload_manage.dest_user.add(address5)
        if dest_user_mail6:
            otp_upload_manage.dest_user.add(address6)
        if dest_user_mail7:
            otp_upload_manage.dest_user.add(address7)
        if dest_user_mail8:
            otp_upload_manage.dest_user.add(address8)

        # 生成されたDBの対象行のIDをセッションに保存しておく
        upload_manage_id = self.kwargs['pk']
        self.request.session['otp_upload_manage_id'] = otp_upload_manage_id

        otp_upload_manage_id_old = self.kwargs['pk']

        # ステップ2へ遷移
        return HttpResponseRedirect(reverse('draganddrop:step2_otp_update', kwargs={'pk': otp_upload_manage_id_old}))

class Step2OTPUpdate(FormView, CommonView):
    model = OTPUploadManage
    template_name = "draganddrop/otp/step2_otp_upload.html"
    form_class = DistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        otp_upload_manage_id = self.kwargs['pk']
        context["otp_upload_manage_id"] = otp_upload_manage_id

        otp_upload_manages = OTPUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["otp_upload_manages"] = otp_upload_manages

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 2

        otp_upload_manage_id_tmp = self.request.session['otp_upload_manage_id']

        otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('file').first()
        files = otp_upload_manage.file.all()
        otp_upload_manage_tmp = OTPUploadManage.objects.filter(pk=otp_upload_manage_id_tmp).prefetch_related('file').first()
        files_tmp = otp_upload_manage_tmp.file.all()

        files = files | files_tmp

        otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('file', 'dest_user').first()
        otp_upload_manage_tmp = OTPUploadManage.objects.filter(pk=otp_upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()

        file = serializers.serialize("json", files, fields=('name', 'size', 'upload', 'id'))
        context["dist_file"] = file


        # URLを返す
        url_name = self.request.resolver_match.url_name
        context["url_name"] = url_name

        context["files"] = files

        return context



    def post(self, request, *args, **kwargs):
        self.del_file = request.POST.getlist('del_file')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        # セッションの対象IDからDBオブジェクトを生成
        otp_upload_manage_id = self.kwargs['pk']
        otp_upload_manage_id_tmp = self.request.session['otp_upload_manage_id']
        otp_upload_manage = OTPUploadManage.objects.get(pk=otp_upload_manage_id)
        otp_upload_manage_tmp = OTPUploadManage.objects.get(pk=otp_upload_manage_id_tmp)


        # 作成日を更新
        otp_upload_manage.created_date = datetime.datetime.now()


        # # ファイルの削除
        if 'del_file_pk' in self.request.session:
            del_file_pk = self.request.session['del_file_pk']

            files = Filemodel.objects.filter(pk__in=del_file_pk)

            for file in files:
                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)
                # ファイルパスを分割してファイル名だけ取得
                file_name = file_path.split('/', 3)[3]
                # パスを取得
                path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                # パスの存在確認
                result = os.path.exists(path)
                if result:
                    # 絶対パスでファイル実体を削除
                    os.remove(os.path.join(
                        settings.FULL_MEDIA_ROOT, file_name))
                # DBの対象行を削除
                file.delete()

        # 保存
        otp_upload_manage.save()

        # 保存
        # upload_manage_tmp.delete()

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
                otp_upload_manage_tmp.file.add(file)
                
                t = threading.Thread

                # PDF変換
                # ①ファイル名から拡張子のみ取得
                file_name = file.name

                file_name_without_dot = os.path.splitext(file_name)[1][1:]
                file_name_no_extention = os.path.splitext(file_name)[0]

                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)

                # ファイルパスを分割してファイル名だけ取得
                file_name = file_path.split('/', 3)[3]

                # パスを取得
                path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)


                # .txtファイルをHTMLファイルへ変換
                # テキストファイルを一括で読み込む
                if file_name_without_dot == "txt":
                    path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                    with open(path) as f:
                        s = f.read()

                        # htmlファイルを生成して書き込む
                        upload_s = str(file.upload)
                        upload_ss = upload_s.split('/')[0]

                        file_path = urllib.parse.unquote(file.upload.url)

                        upload = file_path[1:]
                        upload_path = upload.split('.')
                        path_html = upload_path[0] + ".html"
                        with open(path_html, mode='w') as f:
                            f.write("<html>\n")
                            f.write("<head>\n")
                            f.write("</head>\n")
                            f.write("<body>\n")
                            f.write("<pre>\n")
                            f.write(s)
                            f.write("</pre>\n")
                            f.write("</body>\n")
                            f.write("</html>\n")
                        htmlfilename = path_html
                        htmlname = os.path.basename(htmlfilename)
                        path_html_s = upload_ss + "/" + htmlname
                        htmlfile, created = PDFfilemodel.objects.get_or_create(
                            name=htmlname,
                            size=file.size,
                            upload=path_html_s,
                            file=file
                        )

                        htmlfile.save()


        otp_upload_manage.save()

        # upload_manage_id_old = self.kwargs['pk']

        return HttpResponseRedirect(reverse('draganddrop:step2_otp_update', kwargs={'pk': otp_upload_manage_id}))

class Step3OTPUpdate(TemplateView, CommonView):  # サーバサイドだけの処理
    template_name = 'draganddrop/otp/step3_otp_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        otp_upload_manage_id = self.kwargs['pk']
        otp_upload_manage_id_tmp = self.request.session['otp_upload_manage_id']

        otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('file').first()
        otp_upload_manage_tmp = OTPUploadManage.objects.filter(pk=otp_upload_manage_id_tmp).prefetch_related('file').first()

        # 旧otp_download_tableの取得(新に変更される前に)
        number_of_otp_download_table_old =  OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all().count()

        # 旧otp_download_file_tableの取得
        number_of_otp_download_file_table_old = 0
        for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
                number_of_otp_download_file_table_old += int(otpdownloadtable.otp_download_table.all().count())

        # 旧ファイルの合計サイズ
        otp_upload_manage_file_size_old = 0
        for file in otp_upload_manage.file.all():
            otp_upload_manage_file_size_old = otp_upload_manage_file_size_old + int(file.size)

        #削除対象の送信先を取得・削除

        # アドレス帳から選択したユーザーと直接入力
        dest_user = otp_upload_manage.dest_user.all() #旧データ
        dest_user_tmp = otp_upload_manage_tmp.dest_user.all() #新データ
        delete_dest_users=set(dest_user).difference(set(dest_user_tmp)) #差分の値を取得(新データには含まれていない送信先を特定する)
        for delete_dest_user in delete_dest_users: #set型の要素を個別に取り出す
            otp_downloadtable = OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage, dest_user=delete_dest_user.id) #削除対象の値を取得
            otp_downloadtable.delete()

        # グループ
        dest_user_group = otp_upload_manage.dest_user_group.all() #旧データ
        dest_user_group_tmp = otp_upload_manage_tmp.dest_user_group.all() #新データ
        delete_dest_user_groups=set(dest_user_group).difference(set(dest_user_group_tmp)) #差分の値を取得(新データには含まれていない送信先を特定する)
        for group in delete_dest_user_groups: #set型の要素を個別に取り出す
            for delete_dest_user_group in group.address.all():
                otp_downloadtable = OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage, dest_user=delete_dest_user_group.id) #削除対象の値を取得
                otp_downloadtable.delete()

        #更新データをOTPUploadManageに保存
        otp_upload_manage.title = otp_upload_manage_tmp.title
        otp_upload_manage.end_date = otp_upload_manage_tmp.end_date
        otp_upload_manage.message = otp_upload_manage_tmp.message
        otp_upload_manage.dest_user_mail1 = otp_upload_manage_tmp.dest_user_mail1
        otp_upload_manage.dest_user_mail2 = otp_upload_manage_tmp.dest_user_mail2
        otp_upload_manage.dest_user_mail3 = otp_upload_manage_tmp.dest_user_mail3
        otp_upload_manage.dest_user_mail4 = otp_upload_manage_tmp.dest_user_mail4
        otp_upload_manage.dest_user_mail5 = otp_upload_manage_tmp.dest_user_mail5
        otp_upload_manage.dest_user_mail6 = otp_upload_manage_tmp.dest_user_mail6
        otp_upload_manage.dest_user_mail7 = otp_upload_manage_tmp.dest_user_mail7
        otp_upload_manage.dest_user_mail8 = otp_upload_manage_tmp.dest_user_mail8

        otp_upload_manage.save()

        # 既存ファイルと新ファイルを結合
        otp_upload_manage_file = otp_upload_manage.file.all() | otp_upload_manage_tmp.file.all()

        # Downloadtableへ保存

        # グループに紐付くdownloadtableの作成
        dest_user_groups = otp_upload_manage_tmp.dest_user_group.all()
        for dest_user_group in dest_user_groups:
            for download_user in dest_user_group.address.all():
                otp_downloadtable, created = OTPDownloadtable.objects.get_or_create(otp_upload_manage=otp_upload_manage, dest_user=download_user)
                otp_downloadtable.save()

                # Downloadfiletableへ保存
                for file in otp_upload_manage_file.all():
                    otp_downloadfiletable, created = OTPDownloadFiletable.objects.get_or_create(otp_download_table=otp_downloadtable, download_file = file )
                    otp_downloadfiletable.save()


        # アドレス帳から選択したユーザーと直接入力に紐付くdownloadtableの作成
        for download_user in otp_upload_manage_tmp.dest_user.all():
            otp_downloadtable, created = OTPDownloadtable.objects.get_or_create(otp_upload_manage=otp_upload_manage, dest_user=download_user)
            otp_downloadtable.save()

            # Downloadfiletableへ保存
            for file in otp_upload_manage_file.all():
                otp_downloadfiletable, created = OTPDownloadFiletable.objects.get_or_create(otp_download_table=otp_downloadtable, download_file=file)
                otp_downloadfiletable.save()

        otp_downloadfiletables = OTPDownloadFiletable.objects.filter(otp_download_table=otp_downloadtable).count()
        otp_downloadfiletables_true = OTPDownloadFiletable.objects.filter(
            otp_download_table=otp_downloadtable, is_downloaded=True).count()

        if otp_downloadfiletables == otp_downloadfiletables_true:
            otp_downloadtable.is_downloaded = True

        else:
            otp_downloadtable.is_downloaded = False
            otp_downloadtable.save()

        otp_file_number = OTPDownloadtable.objects.filter(
            otp_upload_manage=otp_downloadtable.otp_upload_manage).count()
        otp_downloaded_file_number = OTPDownloadtable.objects.filter(
            otp_upload_manage=otp_downloadtable.otp_upload_manage, is_downloaded=True).count()

        if otp_file_number == otp_downloaded_file_number:
            otp_downloadtable.otp_upload_manage.is_downloaded = True  # 対応完了

        else:
            otp_upload_manage = otp_downloadtable.otp_upload_manage
            otp_upload_manage.is_downloaded = False
            otp_upload_manage.save()

        otp_downloadtable.save()

        for file in otp_upload_manage_tmp.file.all():
            otp_upload_manage.file.add(file)

        otp_upload_manage.save()

        #全送信先の旧データをremoveして新データをaddする。
        otp_upload_manage.dest_user_group.set(otp_upload_manage_tmp.dest_user_group.all())
        otp_upload_manage.dest_user.set(otp_upload_manage_tmp.dest_user.all())

        # PersonalResourceManagement更新処理
        personal_resource_manage = PersonalResourceManagement.objects.filter(user=self.request.user.id).first()

        # download_tableのレコード数を更新
        number_of_otp_download_table_tmp =  OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all().count()
        personal_resource_manage.number_of_otp_download_table += (number_of_otp_download_table_tmp - number_of_otp_download_table_old)

        # 新ファイルの合計サイズ
        otp_upload_manage_file_size = 0
        for file in otp_upload_manage.file.all():
            otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)
        personal_resource_manage.otp_upload_manage_file_size += (otp_upload_manage_file_size - otp_upload_manage_file_size_old)

        # download_file_tableのレコード数を更新
        number_of_otp_download_file_table_tmp = 0
        for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
            number_of_otp_download_file_table_tmp += int(otpdownloadtable.otp_download_table.all().count())
        personal_resource_manage.number_of_otp_download_file_table += (number_of_otp_download_file_table_tmp - number_of_otp_download_file_table_old)

        personal_resource_manage.save()

        # tmpレコード削除 
        otp_tmp_flag_1 = OTPUploadManage.objects.filter(tmp_flag=1).all()
        otp_tmp_flag_1.delete()

        download_table = personal_resource_manage.number_of_otp_download_table
        download_file_table = personal_resource_manage.number_of_otp_download_file_table
        total_file_size = personal_resource_manage.total_file_size

        # 個人管理テーブルの作成・更新
        total_data_usage(otp_upload_manage, self.request.user.company.id, self.request.user.id, download_table, download_file_table, otp_upload_manage_file_size, 3)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)
        # this_personal_resource_manage.save()

        return context

##################################
# OTPファイルアップロード変更時の戻る処理  #
##################################

class OTPReturnUpdateView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        otp_upload_manage_id_old = self.kwargs['pk']  # 旧データ

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:step1_otp_update', kwargs={'pk': otp_upload_manage_id_old}))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:step1_otp_update', kwargs={'pk': otp_upload_manage_id_old}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:step2_otp_update', kwargs={'pk': otp_upload_manage_id_old}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:step3_otp_update', kwargs={'pk': otp_upload_manage_id_old}))