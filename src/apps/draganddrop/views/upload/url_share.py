from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView
from draganddrop.views.home.home_common import CommonView, total_data_usage, resource_management_calculation_process
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import FileForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksUrlStep1Form, UrlDistFileUploadForm, UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import Filemodel, PDFfilemodel, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.models import ApprovalWorkflow, ApprovalLog, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage
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
from django.core.signing import TimestampSigner, dumps, SignatureExpired
from django.contrib.sites.shortcuts import get_current_site
#操作ログ関数
from lib.my_utils import add_log
#メール送信
from django.core.mail import send_mass_mail
# テンプレート情報取得
from django.template.loader import get_template

Token_LENGTH = 5  # ランダムURLを作成するためのTOKEN

###########################
# URL共有  #
###########################

class Step1UrlUpload(FormView, CommonView):
    model = UrlUploadManage
    template_name = 'draganddrop/url/step1_url_upload.html'
    form_class = ManageTasksUrlStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(Step1UrlUpload, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs

    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'url_upload_manage_id' in self.request.session:
            url_upload_manage_id = self.request.session['url_upload_manage_id']
            url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('dest_user').first()

            initial = {
                'title': url_upload_manage.title,
                'dest_user': url_upload_manage.dest_user.all(),
                'dest_user_group': url_upload_manage.dest_user_group.all(),
                'dest_user_mail1': url_upload_manage.dest_user_mail1,
                'dest_user_mail2': url_upload_manage.dest_user_mail2,
                'dest_user_mail3': url_upload_manage.dest_user_mail3,
                'dest_user_mail4': url_upload_manage.dest_user_mail4,
                'dest_user_mail5': url_upload_manage.dest_user_mail5,
                'dest_user_mail6': url_upload_manage.dest_user_mail6,
                'dest_user_mail7': url_upload_manage.dest_user_mail7,
                'dest_user_mail8': url_upload_manage.dest_user_mail8,
                'end_date': url_upload_manage.end_date,
                'message': url_upload_manage.message,
                'auth_meth': str(url_upload_manage.auth_meth),
                'password': url_upload_manage.password,
                'dl_limit': str(url_upload_manage.dl_limit),
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

        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'url_upload_manage_id' in self.request.session:
            # セッションに存在するテンポラリオブジェクトモデルのIDを取得
            url_upload_manage_id = self.request.session['url_upload_manage_id']

            # モデルオブジェクトを取得
            url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('dest_user').first()

            #context["dest_users"] = upload_manage.dest_user.all()
            # アドレス帳の選択済みユーザー一覧をテンプレートへ渡す
            pk_list = url_upload_manage.dest_user.all().values_list('pk', flat=True)
            context["pk_list"] = list(pk_list)

            group_list = url_upload_manage.dest_user_group.all().values_list('pk', flat=True)
            context["group_list"] = list(group_list)

        return context


    def form_valid(self, form):

        if 'url_upload_manage_id' in self.request.session:
            url_upload_manage_obj = UrlUploadManage.objects.filter(pk=self.request.session['url_upload_manage_id']).prefetch_related('dest_user').first()

        else:
            # フォームからDBのオブジェクトを仮生成（未保存）
            url_upload_manage_obj = form.save(commit=False)

        # # ログインユーザーを登録ユーザーとしてセット
        url_upload_manage_obj.created_user = self.request.user.id
        # # ログインユーザーの会社idをセット
        url_upload_manage_obj.company = self.request.user.company.id
        # # 作成日をセット
        url_upload_manage_obj.created_date = datetime.datetime.now()
        # # テンポラリフラグをセット
        url_upload_manage_obj.tmp_flag = 1
        # アップロード方法をセット
        url_upload_manage_obj.upload_method = 2# URL共有

        # # 保存期日とタイトルに関しても上記と同じように取得
        title = form.cleaned_data['title']
        end_date = form.cleaned_data['end_date']
        auth_meth = form.cleaned_data['auth_meth']
        dl_limit = form.cleaned_data['dl_limit']
        password = form.cleaned_data['password']
        message = form.cleaned_data['message']


        # それぞれをDBに代入
        url_upload_manage_obj.end_date = end_date
        url_upload_manage_obj.title = title
        url_upload_manage_obj.dl_limit = dl_limit
        url_upload_manage_obj.auth_meth = auth_meth
        url_upload_manage_obj.password = password
        url_upload_manage_obj.message = message

        # 保存
        url_upload_manage_obj.save()

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
        url_upload_manage_obj.decode_token = token #tokenをDBに保存
        token_signed = Timestamp_signer.sign(token)  # ランダムURLの生成
        context["token_signed"] = token_signed
        current_site = get_current_site(self.request)
        domain = current_site.domain
        protocol = self.request.scheme
        url_upload_manage_obj.url = protocol + "://" + domain + "/" + "url_check" + "/" + token_signed

        # upload_manageに追加する。データを追加し、戻った際にデータを反映させるため）
        url_upload_manage_obj.dest_user_mail1 = dest_user_mail1
        url_upload_manage_obj.dest_user_mail2 = dest_user_mail2
        url_upload_manage_obj.dest_user_mail3 = dest_user_mail3
        url_upload_manage_obj.dest_user_mail4 = dest_user_mail4
        url_upload_manage_obj.dest_user_mail5 = dest_user_mail5
        url_upload_manage_obj.dest_user_mail6 = dest_user_mail6
        url_upload_manage_obj.dest_user_mail7 = dest_user_mail7
        url_upload_manage_obj.dest_user_mail8 = dest_user_mail8

        # # POSTで送信された設定された宛先ユーザーを取得
        dest_user_qs = form.cleaned_data['dest_user']
        # # MonyToMonyの値はquerysetとして取得するので、set関数を使ってセット
        url_upload_manage_obj.dest_user.set(dest_user_qs)

        dest_user_group_qs = form.cleaned_data['dest_user_group']
        url_upload_manage_obj.dest_user_group.set(dest_user_group_qs)

        if dest_user_mail1:
            url_upload_manage_obj.dest_user.add(address1)
        if dest_user_mail2:
            url_upload_manage_obj.dest_user.add(address2)
        if dest_user_mail3:
            url_upload_manage_obj.dest_user.add(address3)
        if dest_user_mail4:
            url_upload_manage_obj.dest_user.add(address4)
        if dest_user_mail5:
            url_upload_manage_obj.dest_user.add(address5)
        if dest_user_mail6:
            url_upload_manage_obj.dest_user.add(address6)
        if dest_user_mail7:
            url_upload_manage_obj.dest_user.add(address7)
        if dest_user_mail8:
            url_upload_manage_obj.dest_user.add(address8)

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
        self.request.session['dl_limit'] = dl_limit
        self.request.session['auth_meth'] = auth_meth
        self.request.session['password'] = password
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
        url_upload_manage_obj.save()
        url_upload_manage_id = str(url_upload_manage_obj.id)

        # # 生成されたDBの対象行のIDをセッションに保存しておく
        # # upload_manage_id = self.kwargs['pk']
        self.request.session['url_upload_manage_id'] = url_upload_manage_id

        # ステップ2へ遷移(ファイルを選択するステップ)
        return HttpResponseRedirect(reverse('draganddrop:step2_url_upload', kwargs={'pk': url_upload_manage_id}))

class Step2URLupload(LoginRequiredMixin, CreateView, CommonView):
    model = UrlUploadManage
    template_name = "draganddrop/url/step2_url_upload.html"
    form_class = UrlDistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        url_upload_manage_id = self.kwargs['pk']
        context["url_upload_manage_id"] = url_upload_manage_id

        url_upload_manage_obj = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('file').first()
        files = url_upload_manage_obj.file.all()
        context["files"] = files

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

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        url_upload_manage_id = self.kwargs['pk']
        url_upload_manage_obj = UrlUploadManage.objects.filter(pk=url_upload_manage_id).first()

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

                url_upload_manage_obj.file.add(file)

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
                # file_name = file_path.split('/', 3)[3]
                print('----urlのfile_nameはなに',file_name)


                # パスを取得
                # path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                path = os.path.join(settings.FULL_MEDIA_ROOT_FREETMP, file_name)
                print('----urlのpathはなに',path)


                # .txtファイルをHTMLファイルへ変換
                # テキストファイルを一括で読み込む
                # if file_name_without_dot == "txt":
                #     # path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                #     path = os.path.join(settings.FULL_MEDIA_ROOT_FREETMP, file_name)
                #     print('txtふぁいるにすすんだ',path)
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

        url_upload_manage_obj.save()

        return HttpResponseRedirect(reverse('draganddrop:step2_url_upload', kwargs={'pk': url_upload_manage_obj.id}))

class Step3URLupload(TemplateView, CommonView):
    template_name = 'draganddrop/url/step3_url_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        

        print("------------------- URL共有 Step3URLupload")

        url_upload_manage_id = self.kwargs['pk']

        context["url_upload_manage_id"] = url_upload_manage_id

        url_upload_manage_obj = UrlUploadManage.objects.filter(pk=url_upload_manage_id).first()

        url_upload_manage_obj.tmp_flag = 0

        url_upload_manage_obj.save()

        context["url_upload_manage_obj"] = url_upload_manage_obj

        # url_upload_manageに紐付くグループを取得
        dest_user_groups = url_upload_manage_obj.dest_user_group.all()
        for group in dest_user_groups:
            for download_user in group.address.all():
                # ユーザー毎のダウンロード状況を管理するテーブルを作成
                url_downloadtable, created = UrlDownloadtable.objects.get_or_create(url_upload_manage=url_upload_manage_obj, dest_user=download_user)
                url_downloadtable.save()
            
                # UrlDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
                for file in url_upload_manage_obj.file.all():
                    # ファイル毎のダウンロード状況を管理するテーブルを作成
                    url_downloadfiletable, created = UrlDownloadFiletable.objects.get_or_create(url_download_table=url_downloadtable, download_file=file)
                    url_downloadfiletable.download_file = file
                    url_downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        for download_user in url_upload_manage_obj.dest_user.all():
            url_downloadtable, created = UrlDownloadtable.objects.get_or_create(url_upload_manage=url_upload_manage_obj, dest_user=download_user)
            url_downloadtable.save()

            # UrlDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
            for file in url_upload_manage_obj.file.all():
                # ファイル毎のダウンロード状況を管理するテーブルを作成
                url_downloadfiletable, created = UrlDownloadFiletable.objects.get_or_create(url_download_table=url_downloadtable, download_file=file)
                url_downloadfiletable.download_file = file
                url_downloadfiletable.save()

        # PersonalResourceManagementへ保存
        
        # ログインユーザーが作成したurl_upload_manageを取得
        personal_user_url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id).all()
        url_upload_manage_file_size = 0
        download_table = 0
        download_file_table = 0

        for personal_user_url_upload_manage in personal_user_url_upload_manages:

            # ファイルの合計サイズを取得
            for file in personal_user_url_upload_manage.file.all():
                url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)

            # url_download_tableのレコード数を取得
            download_table += UrlDownloadtable.objects.filter(url_upload_manage=personal_user_url_upload_manage).all().count()

            # url_download_file_tableのレコード数を取得
            for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=personal_user_url_upload_manage).all():
                download_file_table += int(urldownloadtable.url_download_table.all().count())

        #操作ログ用
        #送信先取得,アドレス帳＆直接入力
        dest_user =  url_upload_manage_obj.dest_user.values_list('email', flat=True)
        dest_user_list = list(dest_user)
        #送信先グループ取得　OTPとかにも対応  value_listなし<QuerySet [<Group: aaa>]>→value_listあり<QuerySet ['aaa']>
        dest_group = url_upload_manage_obj.dest_user_group.values_list('group_name', flat=True)
        dest_group_list = list(dest_group)
        #送信先　直接入力＆アドレス帳＆グループ list型
        url_dest_users = dest_user_list + dest_group_list
        # ↑の('')を省くため文字列に変換
        url_dest_users = ' '.join(url_dest_users)
        # ファイルタイトル
        file_title = url_upload_manage_obj.title
        # ファイル名
        url_upload_files = url_upload_manage_obj.file.all()
        files = []
        for file in url_upload_files:          
            file_name = file.name + "\r\n"
            files.append(file_name)
        files = ' '.join(files)
        # 操作ログ終わり
        # 操作ログ
        add_log(2,1,current_user,current_user.company,file_title,files,url_dest_users,1,self.request.META.get('REMOTE_ADDR'))

        ###################　Notification通知用  ～を受信しました 操作ログの下にいれる
        #送信先 email
        emailList_db = ','.join(dest_user_list)
        #タイトル
        Notice_title = current_user.display_name + "さんが" + file_title + "を共有しました。"
        #メッセージ
        Notice_message = url_upload_manage_obj.message
        #グループemaillist作成
        group_email = []
        for group in dest_group_list:
            qs = Address.objects.filter(group__group_name=group)
            for user in qs:
                email = user.email
                group_email.append(email)
        group_email_db = ','.join(group_email)
        emailList_for = dest_user_list + group_email #list型
        emailList_db = emailList_db + ',' + group_email_db #str型

        ###通知テーブル登録
        Notification.objects.create(service="FileUP!",category="受信通知",sender=current_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

        #メール送信
        current_site = get_current_site(self.request)
        domain = current_site.domain
        download_type = 'url'
        url = url_upload_manage_obj.url

        tupleMessage = []
        for email in emailList_for:
            e_user = User.objects.filter(email=email).first()
            if e_user:
                e_send = e_user.is_send_mail
            
            if e_user and e_send == True or not e_user:
                context = {
                    'protocol': 'https' if self.request.is_secure() else 'http',
                    'domain': domain,
                    'download_type': download_type,
                    'url': url,
                    #送信者
                    'user_last_name':self.request.user.last_name,
                    'user_first_name':self.request.user.first_name,
                }
                subject_template = get_template('draganddrop/mail_template/subject.txt')
                subject = subject_template.render(context)

                message_template = get_template('draganddrop/mail_template/message.txt')
                message = message_template.render(context)
                from_email = settings.EMAIL_HOST_USER#CL側のメアド
                recipient_list = [email]#受信者リスト
                
                message1 = (
                    subject,
                    message,
                    from_email,
                    recipient_list,
                )
                messageList = list(message1)
                tupleMessage.insert(-1,messageList)

        send_mass_mail(tupleMessage)
        ##################Notification通知用終了

        # 個人管理テーブルの作成・更新
        total_data_usage(url_upload_manage_obj, self.request.user.company.id, self.request.user.id, download_table, download_file_table, url_upload_manage_file_size, 2)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)


        # ユーザーの承認ワークフロー設定を取得
        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        # print("------------------ approval_workflow step2", approval_workflow)

        # 一次承認者を取得
        first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("------------------ first_approvers step2", first_approvers)
        # 二次承認者を取得
        second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        # print("------------------ second_approver step2", second_approvers)


        # 承認ワークフローが「使用する」に設定されている場合
        if approval_workflow.is_approval_workflow == 1:
            # print("------------------ 承認ワークフローが「使用する」に設定されている")

            # 申請ステータスを「申請中」に設定
            url_upload_manage_obj.application_status = 1
            url_upload_manage_obj.save()

            if first_approvers:
                # print("------------------ first_approversがいます step2")
                for first_approver in first_approvers:
                    # ApprovalManageを作成
                    first_approver_approval_manage = ApprovalManage.objects.create(
                        url_upload_manage = url_upload_manage_obj,
                        manage_id = url_upload_manage_obj.id,
                        application_title = url_upload_manage_obj.title,
                        application_user = url_upload_manage_obj.created_user,
                        application_date = url_upload_manage_obj.created_date,
                        application_user_company_id = url_upload_manage_obj.company,
                        approval_status = 1,
                        first_approver = first_approver.first_approver,
                        upload_method = 2 # URL共有
                    )
                    first_approver_approval_manage.save()

            if second_approvers:
                # print("------------------ second_approversがいます step2")
                for second_approver in second_approvers:
                    # ApprovalManageを作成
                    second_approver_approval_manage = ApprovalManage.objects.create(
                        url_upload_manage = url_upload_manage_obj,
                        manage_id = url_upload_manage_obj.id,
                        application_title = url_upload_manage_obj.title,
                        application_user = url_upload_manage_obj.created_user,
                        application_date = url_upload_manage_obj.created_date,
                        application_user_company_id = url_upload_manage_obj.company,
                        approval_status = 1,
                        second_approver = second_approver.second_approver,
                        upload_method = 2 # URL共有
                    )
                    second_approver_approval_manage.save()

        # 使用しない場合 承認済みのApprovalManageを作成
        else:
            # print("------------------ 承認ワークフローが「使用しない」に設定されている")

            if first_approvers:
                # print("------------------ first_approversがいます step2")

                # 申請ステータスを「一次承認済み」に設定
                url_upload_manage_obj.application_status = 3
                url_upload_manage_obj.save()

                for first_approver in first_approvers:
                    # ApprovalManageを作成
                    first_approver_approval_manage = ApprovalManage.objects.create(
                        url_upload_manage = url_upload_manage_obj,
                        manage_id = url_upload_manage_obj.pk,
                        application_title = url_upload_manage_obj.title,
                        application_user = url_upload_manage_obj.created_user,
                        application_date = url_upload_manage_obj.created_date,
                        application_user_company_id = url_upload_manage_obj.company,
                        approval_status = 2, # 一次承認済み
                        first_approver = first_approver.first_approver,
                        upload_method = 2 # URL共有
                    )
                    first_approver_approval_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        url_upload_manage = url_upload_manage_obj,
                        approval_operation_user = first_approver.first_approver,
                        approval_operation_user_position = 1, # 一次承認者
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date =  url_upload_manage_obj.created_date,
                        approval_operation_content = 2, # 一次承認
                        manage_id = url_upload_manage_obj.pk
                    )
                    approval_log.save()

            if second_approvers:
                # print("------------------ second_approversがいます step2")

                # 申請ステータスを「最終承認済み」に設定
                url_upload_manage_obj.application_status = 5
                url_upload_manage_obj.save()

                for second_approver in second_approvers:
                    # ApprovalManageを作成
                    second_approver_approval_manage = ApprovalManage.objects.create(
                        url_upload_manage = url_upload_manage_obj,
                        manage_id = url_upload_manage_obj.pk,
                        application_title = url_upload_manage_obj.title,
                        application_user = url_upload_manage_obj.created_user,
                        application_date = url_upload_manage_obj.created_date,
                        application_user_company_id = url_upload_manage_obj.company,
                        approval_status = 3, # 最終承認済み
                        second_approver = second_approver.second_approver,
                        upload_method = 2 # URL共有
                    )
                    second_approver_approval_manage.save()

                    # 承認履歴を残す
                    approval_log = ApprovalLog.objects.create(
                        url_upload_manage = url_upload_manage_obj,
                        approval_operation_user = second_approver.second_approver,
                        approval_operation_user_position = 2, # 二次承認者
                        approval_operation_user_company_id = self.request.user.company.id,
                        approval_operation_date =  url_upload_manage_obj.created_date,
                        approval_operation_content = 3, # 最終承認
                        manage_id = url_upload_manage_obj.pk
                    )
                    approval_log.save()

        return context

##################################
# URLファイル共有登録時の戻る処理 #
##################################

class UrlReturnView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        url_upload_manage_id = self.kwargs['pk']  # 旧データ

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:step1_url_upload'))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:step2_url_upload', kwargs={'pk': url_upload_manage_id}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:step3_url_upload', kwargs={'pk': url_upload_manage_id}))



###########################
# URL共有 アップデート   #
###########################

class Step1UrlUpdate(FormView, CommonView):
    model = UrlUploadManage
    template_name = 'draganddrop/url/step1_url_upload.html'
    form_class = ManageTasksUrlStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(Step1UrlUpdate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs

    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        url_upload_manage_id = self.kwargs['pk']
        if 'url_upload_manage_id' in self.request.session:
            url_upload_manage = UrlUploadManage.objects.filter(pk=self.request.session['url_upload_manage_id']).first()  # 新データ

            dest_user_mail1 = url_upload_manage.dest_user_mail1
            dest_user_mail2 = url_upload_manage.dest_user_mail2
            dest_user_mail3 = url_upload_manage.dest_user_mail3
            dest_user_mail4 = url_upload_manage.dest_user_mail4
            dest_user_mail5 = url_upload_manage.dest_user_mail5
            dest_user_mail6 = url_upload_manage.dest_user_mail6
            dest_user_mail7 = url_upload_manage.dest_user_mail7
            dest_user_mail8 = url_upload_manage.dest_user_mail8
            dest_user = url_upload_manage.dest_user
            dest_user_group = url_upload_manage.dest_user_group
            title = url_upload_manage.title
            dl_limit = url_upload_manage.dl_limit
            end_date = url_upload_manage.end_date
            auth_meth = url_upload_manage.auth_meth
            password = url_upload_manage.password
            message = url_upload_manage.message

            if url_upload_manage.dest_user.all().count() == 0:
                url_upload_manage_old = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
                dest_user = url_upload_manage_old.dest_user.all()
            else:
                dest_user = url_upload_manage.dest_user.all()

            if url_upload_manage.dest_user_group.all().count() == 0:
                url_upload_manage_old = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('dest_user_group',).first()  # 旧データ
                dest_user_group = url_upload_manage_old.dest_user_group.all()
            else:
                dest_user_group = url_upload_manage.dest_user_group.all()

            if url_upload_manage.end_date == None:
                url_upload_manage_old = UrlUploadManage.objects.filter(pk=url_upload_manage_id).first()  # 旧データ
                end_date = url_upload_manage_old.end_date
            else:
                end_date = url_upload_manage.end_date

            if url_upload_manage.dl_limit == None:
                url_upload_manage_old = UrlUploadManage.objects.filter(pk=url_upload_manage_id).first()  # 旧データ
                dl_limit = url_upload_manage_old.dl_limit
            else:
                dl_limit = url_upload_manage.dl_limit

            if url_upload_manage.auth_meth == None:
                url_upload_manage_old = UrlUploadManage.objects.filter(pk=url_upload_manage_id).first()  # 旧データ
                auth_meth = url_upload_manage_old.auth_meth
            else:
                auth_meth = url_upload_manage.auth_meth

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
                        'dl_limit': dl_limit,
                        'end_date': end_date,
                        'auth_meth': auth_meth,
                        'password': password,
                        'message': message
                    }

        # formに新たな値が書き込まれなかった時に元の旧データを返す処理。
        else:
            url_upload_manage_old = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
            initial = {
                        'title': url_upload_manage_old.title,
                        'dest_user': url_upload_manage_old.dest_user.all(),
                        'dest_user_group': url_upload_manage_old.dest_user_group.all(),
                        'dest_user_mail1': url_upload_manage_old.dest_user_mail1,
                        'dest_user_mail2': url_upload_manage_old.dest_user_mail2,
                        'dest_user_mail3': url_upload_manage_old.dest_user_mail3,
                        'dest_user_mail4': url_upload_manage_old.dest_user_mail4,
                        'dest_user_mail5': url_upload_manage_old.dest_user_mail5,
                        'dest_user_mail6': url_upload_manage_old.dest_user_mail6,
                        'dest_user_mail7': url_upload_manage_old.dest_user_mail7,
                        'dest_user_mail8': url_upload_manage_old.dest_user_mail8,
                        'end_date': url_upload_manage_old.end_date,
                        'dl_limit': url_upload_manage_old.dl_limit,
                        'password': url_upload_manage_old.password,
                        'auth_meth': url_upload_manage_old.auth_meth,
                        'message': url_upload_manage_old.message,
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


        url_upload_manage_id = self.kwargs['pk']
        if 'url_upload_manage_id' in self.request.session:
            url_upload_manage = UrlUploadManage.objects.filter(pk=self.request.session['url_upload_manage_id']).first()  # 新データ
        else:
            url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('dest_user').first()
        
        context["dest_users"] = url_upload_manage.dest_user.all()

        dest_user_qs = url_upload_manage.dest_user.all().order_by('pk')
        full_name_list = []
        for dest_user in dest_user_qs:
            full_name = dest_user.last_name + " " + dest_user.first_name
            full_name_list.append(full_name)
        context["name"] = full_name_list

        company_name = dest_user_qs.values_list('company_name', flat=True)
        context["company_name"] = list(company_name)

        pk_list = dest_user_qs.values_list('pk', flat=True)
        context["pk_list"] = list(pk_list)

        dest_user_group_qs = url_upload_manage.dest_user_group.all().order_by('pk')
        group_list = dest_user_group_qs.values_list('pk', flat=True)
        context["group_list"] = list(group_list)

        return context

    def form_valid(self, form):

        if 'url_upload_manage_id' in self.request.session:
            url_upload_manage = UrlUploadManage.objects.filter(pk=self.request.session['url_upload_manage_id']).first()

        else:
            # セッションに値がない場合新たにカラムを作成する。
            url_upload_manage = form.save(commit=False)

        title = form.cleaned_data['title']
        end_date = form.cleaned_data['end_date']
        auth_meth = form.cleaned_data['auth_meth']
        dl_limit = form.cleaned_data['dl_limit']
        password = form.cleaned_data['password']
        message = form.cleaned_data['message']
        dest_user_qs = form.cleaned_data['dest_user']
        dest_user_group_qs = form.cleaned_data['dest_user_group']


        # ログインユーザーを登録ユーザーとしてセット
        url_upload_manage.created_user = self.request.user.id
        # ログインユーザーの会社idをセット
        url_upload_manage.company = self.request.user.company.id
        # 作成日をセット
        url_upload_manage.created_date = datetime.datetime.now()
        # テンポラリフラグをセット
        url_upload_manage.tmp_flag = 1
        # タイトルをセット
        url_upload_manage.title = title
        # 終了日をセット
        url_upload_manage.end_date = end_date
        # ダウンロード回数をセット
        url_upload_manage.dl_limit = dl_limit
        # パスワードをセット
        url_upload_manage.password = password
        # 認証方法をセット
        url_upload_manage.auth_meth = auth_meth
        # メッセージをセット
        url_upload_manage.message = message


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
        url_upload_manage.dest_user_mail1 = dest_user_mail1
        url_upload_manage.dest_user_mail2 = dest_user_mail2
        url_upload_manage.dest_user_mail3 = dest_user_mail3
        url_upload_manage.dest_user_mail4 = dest_user_mail4
        url_upload_manage.dest_user_mail5 = dest_user_mail5
        url_upload_manage.dest_user_mail6 = dest_user_mail6
        url_upload_manage.dest_user_mail7 = dest_user_mail7
        url_upload_manage.dest_user_mail8 = dest_user_mail8

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
        self.request.session['dl_limit'] = dl_limit
        self.request.session['auth_meth'] = auth_meth
        self.request.session['password'] = password
        self.request.session['message'] = message
        self.request.session['dest_user_all_list'] = dest_user_all_list

        url_upload_manage.save()
        url_upload_manage_id = str(url_upload_manage.id)


        # # MonyToMonyの値はquerysetとして取得するのでupload_manageに保存したうえで、set関数を使ってセット
        url_upload_manage.dest_user.set(dest_user_qs)
        url_upload_manage.dest_user_group.set(dest_user_group_qs)

        if dest_user_mail1:
            url_upload_manage.dest_user.add(address1)
        if dest_user_mail2:
            url_upload_manage.dest_user.add(address2)
        if dest_user_mail3:
            url_upload_manage.dest_user.add(address3)
        if dest_user_mail4:
            url_upload_manage.dest_user.add(address4)
        if dest_user_mail5:
            url_upload_manage.dest_user.add(address5)
        if dest_user_mail6:
            url_upload_manage.dest_user.add(address6)
        if dest_user_mail7:
            url_upload_manage.dest_user.add(address7)
        if dest_user_mail8:
            url_upload_manage.dest_user.add(address8)

        # 生成されたDBの対象行のIDをセッションに保存しておく
        upload_manage_id = self.kwargs['pk']
        self.request.session['url_upload_manage_id'] = url_upload_manage_id

        url_upload_manage_id_old = self.kwargs['pk']

        # ステップ2へ遷移
        return HttpResponseRedirect(reverse('draganddrop:step2_url_update', kwargs={'pk': url_upload_manage_id_old}))

class Step2UrlUpdate(FormView, CommonView):
    model = UrlUploadManage
    template_name = "draganddrop/url/step2_url_upload.html"
    form_class = DistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        url_upload_manage_id = self.kwargs['pk']
        context["url_upload_manage_id"] = url_upload_manage_id

        url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["url_upload_manages"] = url_upload_manages

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 2

        url_upload_manage_id_tmp = self.request.session['url_upload_manage_id']

        url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('file').first()
        files = url_upload_manage.file.all()
        url_upload_manage_tmp = UrlUploadManage.objects.filter(pk=url_upload_manage_id_tmp).prefetch_related('file').first()
        files_tmp = url_upload_manage_tmp.file.all()

        files = files | files_tmp

        url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('file', 'dest_user').first()
        url_upload_manage_tmp = UrlUploadManage.objects.filter(pk=url_upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()

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
        url_upload_manage_id = self.kwargs['pk']
        url_upload_manage_id_tmp = self.request.session['url_upload_manage_id']
        url_upload_manage = UrlUploadManage.objects.get(pk=url_upload_manage_id)
        url_upload_manage_tmp = UrlUploadManage.objects.get(pk=url_upload_manage_id_tmp)


        # 作成日を更新
        url_upload_manage.created_date = datetime.datetime.now()


        # # ファイルの削除
        if 'del_file_pk' in self.request.session:
            del_file_pk = self.request.session['del_file_pk']

            files = UrlFilemodel.objects.filter(pk__in=del_file_pk)

            for file in files:
                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)
                # ファイルパスを分割してファイル名だけ取得
                file_name = file_path.split('/', 3)[3]
                # file_name = file_path.split('/', 2)[2]
                
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
        url_upload_manage.save()

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
                url_upload_manage_tmp.file.add(file)
                
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
                # file_name = file_path.split('/', 2)[2]
                

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


        url_upload_manage.save()

        # upload_manage_id_old = self.kwargs['pk']

        return HttpResponseRedirect(reverse('draganddrop:step2_url_update', kwargs={'pk': url_upload_manage_id}))

class Step3UrlUpdate(TemplateView, CommonView):  # サーバサイドだけの処理
    template_name = 'draganddrop/url/step3_url_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        url_upload_manage_id = self.kwargs['pk']
        url_upload_manage_id_tmp = self.request.session['url_upload_manage_id']

        url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('file').first()
        url_upload_manage_tmp = UrlUploadManage.objects.filter(pk=url_upload_manage_id_tmp).prefetch_related('file').first()

        # 旧url_download_tableの取得(新に変更される前に)
        number_of_url_download_table_old =  UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all().count()

        # 旧url_download_file_tableの取得
        number_of_url_download_file_table_old = 0
        for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
                number_of_url_download_file_table_old += int(urldownloadtable.url_download_table.all().count())
        
        # 旧ファイルの合計サイズ
        url_upload_manage_file_size_old = 0
        for file in url_upload_manage.file.all():
            url_upload_manage_file_size_old = url_upload_manage_file_size_old + int(file.size)

        #削除対象の送信先を取得・削除

        # アドレス帳から選択したユーザーと直接入力
        dest_user = url_upload_manage.dest_user.all() #旧データ
        dest_user_tmp = url_upload_manage_tmp.dest_user.all() #新データ
        delete_dest_users=set(dest_user).difference(set(dest_user_tmp)) #差分の値を取得(新データには含まれていない送信先を特定する)
        for delete_dest_user in delete_dest_users: #set型の要素を個別に取り出す
            url_downloadtable = UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage, dest_user=delete_dest_user.id) #削除対象の値を取得
            url_downloadtable.delete()

        # グループ
        dest_user_group = url_upload_manage.dest_user_group.all() #旧データ
        dest_user_group_tmp = url_upload_manage_tmp.dest_user_group.all() #新データ
        delete_dest_user_groups=set(dest_user_group).difference(set(dest_user_group_tmp)) #差分の値を取得(新データには含まれていない送信先を特定する)
        for group in delete_dest_user_groups: #set型の要素を個別に取り出す
            for delete_dest_user_group in group.address.all():
                url_downloadtable = UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage, dest_user=delete_dest_user_group.id) #削除対象の値を取得
                url_downloadtable.delete()

        #更新データをUrlUploadManageに保存
        url_upload_manage.title = url_upload_manage_tmp.title
        url_upload_manage.end_date = url_upload_manage_tmp.end_date
        url_upload_manage.dl_limit = url_upload_manage_tmp.dl_limit
        url_upload_manage.auth_meth = url_upload_manage_tmp.auth_meth
        url_upload_manage.password = url_upload_manage_tmp.password
        url_upload_manage.message = url_upload_manage_tmp.message
        url_upload_manage.dest_user_mail1 = url_upload_manage_tmp.dest_user_mail1
        url_upload_manage.dest_user_mail2 = url_upload_manage_tmp.dest_user_mail2
        url_upload_manage.dest_user_mail3 = url_upload_manage_tmp.dest_user_mail3
        url_upload_manage.dest_user_mail4 = url_upload_manage_tmp.dest_user_mail4
        url_upload_manage.dest_user_mail5 = url_upload_manage_tmp.dest_user_mail5
        url_upload_manage.dest_user_mail6 = url_upload_manage_tmp.dest_user_mail6
        url_upload_manage.dest_user_mail7 = url_upload_manage_tmp.dest_user_mail7
        url_upload_manage.dest_user_mail8 = url_upload_manage_tmp.dest_user_mail8
        
        url_upload_manage.save()

        # 既存ファイルと新ファイルを結合
        url_upload_manage_file = url_upload_manage.file.all() | url_upload_manage_tmp.file.all()

        # Downloadtableへ保存

        # グループに紐付くdownloadtableの作成
        dest_user_groups = url_upload_manage_tmp.dest_user_group.all()
        for dest_user_group in dest_user_groups:
            for download_user in dest_user_group.address.all():
                url_downloadtable, created = UrlDownloadtable.objects.get_or_create(url_upload_manage=url_upload_manage, dest_user=download_user)
                url_downloadtable.save()

                # Downloadfiletableへ保存
                for file in url_upload_manage_file.all():
                    url_downloadfiletable, created = UrlDownloadFiletable.objects.get_or_create(url_download_table=url_downloadtable, download_file = file )
                    url_downloadfiletable.save()


        # アドレス帳から選択したユーザーと直接入力に紐付くdownloadtableの作成
        for download_user in url_upload_manage_tmp.dest_user.all():
            url_downloadtable, created = UrlDownloadtable.objects.get_or_create(url_upload_manage=url_upload_manage, dest_user=download_user)
            url_downloadtable.save()
            
            # Downloadfiletableへ保存
            for file in url_upload_manage_file.all():
                url_downloadfiletable, created = UrlDownloadFiletable.objects.get_or_create(url_download_table=url_downloadtable, download_file=file)
                url_downloadfiletable.save()

        url_downloadfiletables = UrlDownloadFiletable.objects.filter(url_download_table=url_downloadtable).count()
        url_downloadfiletables_true = UrlDownloadFiletable.objects.filter(
            url_download_table=url_downloadtable, is_downloaded=True).count()

        if url_downloadfiletables == url_downloadfiletables_true:
            url_downloadtable.is_downloaded = True

        else:
            url_downloadtable.is_downloaded = False
            url_downloadtable.save()

        url_file_number = UrlDownloadtable.objects.filter(
            url_upload_manage=url_downloadtable.url_upload_manage).count()
        url_downloaded_file_number = UrlDownloadtable.objects.filter(
            url_upload_manage=url_downloadtable.url_upload_manage, is_downloaded=True).count()

        if url_file_number == url_downloaded_file_number:
            url_downloadtable.url_upload_manage.is_downloaded = True  # 対応完了

        else:
            url_upload_manage = url_downloadtable.url_upload_manage
            url_upload_manage.is_downloaded = False
            url_upload_manage.save()

        url_downloadtable.save()

        for file in url_upload_manage_tmp.file.all():
            url_upload_manage.file.add(file)

        url_upload_manage.save()

        #全送信先の旧データをremoveして新データをaddする。
        url_upload_manage.dest_user_group.set(url_upload_manage_tmp.dest_user_group.all())
        url_upload_manage.dest_user.set(url_upload_manage_tmp.dest_user.all())
        
        # PersonalResourceManagement更新処理
        personal_resource_manage = PersonalResourceManagement.objects.filter(user=self.request.user.id).first()

        # download_tableのレコード数を更新
        number_of_url_download_table_tmp =  UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all().count()
        personal_resource_manage.number_of_url_download_table += (number_of_url_download_table_tmp - number_of_url_download_table_old)

        # 新ファイルの合計サイズ
        url_upload_manage_file_size = 0
        for file in url_upload_manage.file.all():
            url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)
        personal_resource_manage.url_upload_manage_file_size += (url_upload_manage_file_size - url_upload_manage_file_size_old)
        
        # download_file_tableのレコード数を更新
        number_of_url_download_file_table_tmp = 0
        for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
            number_of_url_download_file_table_tmp += int(urldownloadtable.url_download_table.all().count())
        personal_resource_manage.number_of_url_download_file_table += (number_of_url_download_file_table_tmp - number_of_url_download_file_table_old)
        
        personal_resource_manage.save()

        # tmpレコード削除 
        url_tmp_flag_1 = UrlUploadManage.objects.filter(tmp_flag=1).all()
        url_tmp_flag_1.delete()

        download_table = personal_resource_manage.number_of_url_download_table
        download_file_table = personal_resource_manage.number_of_url_download_file_table
        total_file_size = personal_resource_manage.total_file_size

        #操作ログ用
        #送信先取得,アドレス帳＆直接入力
        dest_user =  url_upload_manage.dest_user.values_list('email', flat=True)
        dest_user_list = list(dest_user)
        #送信先グループ取得　OTPとかにも対応  value_listなし<QuerySet [<Group: aaa>]>→value_listあり<QuerySet ['aaa']>
        dest_group = url_upload_manage.dest_user_group.values_list('group_name', flat=True)
        dest_group_list = list(dest_group)
        #送信先　直接入力＆アドレス帳＆グループ list型
        dest_users = dest_user_list + dest_group_list
        # ↑の('')を省くため文字列に変換
        dest_users = ' '.join(dest_users)
        # ファイルタイトル
        file_title = url_upload_manage.title
        # ファイル名
        url_upload_files = url_upload_manage.file.all()
        files = []
        for file in url_upload_files:         
            file_name = file.name + "\r\n"
            files.append(file_name)
        files = ' '.join(files)
        # 操作ログ終わり
        # 操作ログ
        add_log(2,2,current_user,current_user.company,file_title,files,dest_users,1,self.request.META.get('REMOTE_ADDR'))

        # ApprovalManageを取得
        approval_manages = ApprovalManage.objects.filter(url_upload_manage=url_upload_manage)
        for approval_manage in approval_manages:
            # 値を更新
            approval_manage.application_title = url_upload_manage.title
            approval_manage.application_date = url_upload_manage.created_date
            approval_manage.save()

        ###################　Notification通知用  ～を変更しました 操作ログの下にいれる
        #送信先 email
        emailList_db = ','.join(dest_user_list)
        #タイトル
        Notice_title = current_user.display_name + "さんが" + file_title + "を変更しました。"
        #メッセージ
        Notice_message = url_upload_manage.message
        #グループemaillist作成
        group_email = []
        for group in dest_group_list:
            qs = Address.objects.filter(group__group_name=group)
            for user in qs:
                email = user.email
                group_email.append(email)
        group_email_db = ','.join(group_email)
        emailList_for = dest_user_list + group_email #list型
        emailList_db = emailList_db + ',' + group_email_db #str型

        ###通知テーブル登録
        Notification.objects.create(service="FileUP!",category="受信通知",sender=current_user,title=Notice_title,email_list=emailList_db,fileup_title=file_title,contents=Notice_message)

        #メール送信
        current_site = get_current_site(self.request)
        domain = current_site.domain
        download_type = 'url'
        url = url_upload_manage.url

        tupleMessage = []
        for email in emailList_for:
            e_user = User.objects.filter(email=email).first()
            if e_user:
                e_send = e_user.is_send_mail

            if e_user and e_send == True or not e_user:
                context = {
                    'protocol': 'https' if self.request.is_secure() else 'http',
                    'domain': domain,
                    'download_type': download_type,
                    'url': url,
                    #送信者
                    'user_last_name':self.request.user.last_name,
                    'user_first_name':self.request.user.first_name,
                }
                subject_template = get_template('draganddrop/mail_template/update_subject.txt')
                subject = subject_template.render(context)

                message_template = get_template('draganddrop/mail_template/update_message.txt')
                message = message_template.render(context)
                from_email = settings.EMAIL_HOST_USER#CL側のメアド
                recipient_list = [email]#受信者リスト
                
                message1 = (
                    subject,
                    message,
                    from_email,
                    recipient_list,
                )
                messageList = list(message1)
                tupleMessage.insert(-1,messageList)

            # send_mail(subject, message, from_email, recipient_list)
        send_mass_mail(tupleMessage)
        ##################Notification通知用終了
        # 個人管理テーブルの作成・更新
        total_data_usage(url_upload_manage, self.request.user.company.id, self.request.user.id, download_table, download_file_table, url_upload_manage_file_size, 2)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)
        # this_personal_resource_manage.save()

        return context

##################################
# URLファイルアップロード変更時の戻る処理  #
##################################

class UrlReturnUpdateView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        url_upload_manage_id_old = self.kwargs['pk']  # 旧データ

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:step1_url_update', kwargs={'pk': url_upload_manage_id_old}))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:step1_url_update', kwargs={'pk': url_upload_manage_id_old}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:step2_url_update', kwargs={'pk': url_upload_manage_id_old}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:step3_url_update', kwargs={'pk': url_upload_manage_id_old}))