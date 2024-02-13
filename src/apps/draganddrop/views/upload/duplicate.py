from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView
from draganddrop.views.home.home_common import CommonView, total_data_usage, resource_management_calculation_process
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import FileForm, ManageTasksStep1Form, DummyForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksUrlStep1Form, UrlDistFileUploadForm, ManageTasksOTPStep1Form, OTPDistFileUploadForm, UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, OTPUploadManage, OTPDownloadtable, OTPDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage
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
# 複製機能  #
###########################
"""
アップロード 複製
"""
class DuplicateStep1(FormView, CommonView):
    model = UploadManage
    template_name = 'draganddrop/duplicate/duplicate_step1.html'
    form_class = ManageTasksStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(DuplicateStep1, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs

    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        upload_manage_id = self.kwargs['pk']
        if 'upload_manage_id' in self.request.session:
            upload_manage = UploadManage.objects.filter(pk=self.request.session['upload_manage_id']).first()  # 新データ

            dest_user_mail1 = upload_manage.dest_user_mail1
            dest_user_mail2 = upload_manage.dest_user_mail2
            dest_user_mail3 = upload_manage.dest_user_mail3
            dest_user_mail4 = upload_manage.dest_user_mail4
            dest_user_mail5 = upload_manage.dest_user_mail5
            dest_user_mail6 = upload_manage.dest_user_mail6
            dest_user_mail7 = upload_manage.dest_user_mail7
            dest_user_mail8 = upload_manage.dest_user_mail8
            dest_user = upload_manage.dest_user
            dest_user_group = upload_manage.dest_user_group
            title = upload_manage.title
            dl_limit = upload_manage.dl_limit
            end_date = upload_manage.end_date
            message = upload_manage.message

            if upload_manage.dest_user.all().count() == 0:
                upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
                dest_user = upload_manage_old.dest_user.all()
            else:
                dest_user = upload_manage.dest_user.all()
            
            if upload_manage.dest_user_group.all().count() == 0:
                upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user_group',).first()  # 旧データ
                dest_user_group = upload_manage_old.dest_user_group.all()
            else:
                dest_user_group = upload_manage.dest_user_group.all()

            if upload_manage.end_date == None:
                upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).first()  # 旧データ
                end_date = upload_manage_old.end_date
            else:
                end_date = upload_manage.end_date

            if upload_manage.dl_limit == None:
                upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).first()  # 旧データ
                dl_limit = upload_manage_old.dl_limit
            else:
                dl_limit = upload_manage.dl_limit
            
            if upload_manage.message == None:
                upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).first()  # 旧データ
                dl_limit = upload_manage_old.message
            else:
                dl_limit = upload_manage.message

            initial = {'title': title,
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
                        'message': message
                        }

        # formに新たな値が書き込まれなかった時に元の旧データを返す処理。
        else:
            upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
            initial = {'title': upload_manage_old.title + "_copy",
                        'dest_user': upload_manage_old.dest_user.all(),
                        'dest_user_group': upload_manage_old.dest_user_group.all(),
                        'dest_user_mail1': upload_manage_old.dest_user_mail1,
                        'dest_user_mail2': upload_manage_old.dest_user_mail2,
                        'dest_user_mail3': upload_manage_old.dest_user_mail3,
                        'dest_user_mail4': upload_manage_old.dest_user_mail4,
                        'dest_user_mail5': upload_manage_old.dest_user_mail5,
                        'dest_user_mail6': upload_manage_old.dest_user_mail6,
                        'dest_user_mail7': upload_manage_old.dest_user_mail7,
                        'dest_user_mail8': upload_manage_old.dest_user_mail8,
                        'end_date': upload_manage_old.end_date,
                        'dl_limit': upload_manage_old.dl_limit,
                        'message': upload_manage_old.message
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

        upload_manage_id = self.kwargs['pk']
        if 'upload_manage_id' in self.request.session:
            upload_manage = UploadManage.objects.filter(pk=self.request.session['upload_manage_id']).first()  # 新データ
        else:
            upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user').first()

        context["dest_users"] = upload_manage.dest_user.all()

        dest_user_qs = upload_manage.dest_user.all().order_by('pk')

        full_name_list = []
        for dest_user in dest_user_qs:
            full_name = dest_user.last_name + " " + dest_user.first_name
            full_name_list.append(full_name)
        context["name"] = full_name_list

        company_name = dest_user_qs.values_list('company_name', flat=True)
        context["company_name"] = list(company_name)

        pk_list = dest_user_qs.values_list('pk', flat=True)
        context["pk_list"] = list(pk_list)

        dest_user_group_qs = upload_manage.dest_user_group.all().order_by('pk')
        group_list = dest_user_group_qs.values_list('pk', flat=True)
        context["group_list"] = list(group_list)


        return context

    # フォームが有効な場合指定されたURLへダイレクトする。
    # データがポストされた時に呼ばれるメソッド
    def form_valid(self, form):

        if 'upload_manage_id' in self.request.session:
            upload_manage = UploadManage.objects.filter(pk=self.request.session['upload_manage_id']).first()

        else:
            # セッションに値がない場合新たにカラムを作成する。
            upload_manage = form.save(commit=False)

        title = form.cleaned_data['title']
        end_date = form.cleaned_data['end_date']
        dl_limit = form.cleaned_data['dl_limit']
        message = form.cleaned_data['message']
        dest_user_qs = form.cleaned_data['dest_user']
        dest_user_group_qs = form.cleaned_data['dest_user_group']

        # ログインユーザーを登録ユーザーとしてセット
        upload_manage.created_user = self.request.user.id
        # ログインユーザーの会社idをセット
        upload_manage.company = self.request.user.company.id
        # 作成日をセット
        upload_manage.created_date = datetime.datetime.now()
        # テンポラリフラグをセット
        upload_manage.tmp_flag = 1
        # 終了日をセット
        upload_manage.end_date = end_date
        # ダウンロード回数をセット
        upload_manage.dl_limit = dl_limit
        # メッセージをセット
        upload_manage.message = message
        # アップロード方法をセット
        upload_manage.upload_method = 1 # 通常アップロード

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
        upload_manage.dest_user_mail1 = dest_user_mail1
        upload_manage.dest_user_mail2 = dest_user_mail2
        upload_manage.dest_user_mail3 = dest_user_mail3
        upload_manage.dest_user_mail4 = dest_user_mail4
        upload_manage.dest_user_mail5 = dest_user_mail5
        upload_manage.dest_user_mail6 = dest_user_mail6
        upload_manage.dest_user_mail7 = dest_user_mail7
        upload_manage.dest_user_mail8 = dest_user_mail8

        # dest_userをsessionに追加するためQSをリスト化して保存。
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

        # 日付をString化
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        # POST送信された情報をセッションへ保存
        self.request.session['title'] = title
        self.request.session['end_date'] = end_date
        self.request.session['dl_limit'] = dl_limit
        self.request.session['message'] = message
        self.request.session['dest_user_all_list'] = dest_user_all_list

        upload_manage.save()
        upload_manage_id = str(upload_manage.id)

        # # MonyToMonyの値はquerysetとして取得するのでupload_manageに保存したうえで、set関数を使ってセット
        upload_manage.dest_user.set(dest_user_qs)
        upload_manage.dest_user_group.set(dest_user_group_qs)

        if dest_user_mail1:
            upload_manage.dest_user.add(address1)
        if dest_user_mail2:
            upload_manage.dest_user.add(address2)
        if dest_user_mail3:
            upload_manage.dest_user.add(address3)
        if dest_user_mail4:
            upload_manage.dest_user.add(address4)
        if dest_user_mail5:
            upload_manage.dest_user.add(address5)
        if dest_user_mail6:
            upload_manage.dest_user.add(address6)
        if dest_user_mail7:
            upload_manage.dest_user.add(address7)
        if dest_user_mail8:
            upload_manage.dest_user.add(address8)

        # 生成されたDBの対象行のIDをセッションに保存しておく
        self.request.session['upload_manage_id'] = upload_manage_id

        upload_manage_id_old = self.kwargs['pk']

        # ステップ2へ遷移
        return HttpResponseRedirect(reverse('draganddrop:duplicate_step2', kwargs={'pk': upload_manage_id_old}))

class DuplicateStep2(FormView, CommonView):
    model = UploadManage
    template_name = "draganddrop/duplicate/duplicate_step2.html"
    form_class = DistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        original_upload_manage_id = self.kwargs['pk'] #複製元データ
        context["upload_manage_id"] = original_upload_manage_id
        
        upload_manage_id_tmp = self.request.session['upload_manage_id'] #複製データ

        upload_manage_tmp = UploadManage.objects.filter(pk=upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()
        number_of_files = upload_manage_tmp.file.filter(del_flag=0).all().count()
        if number_of_files == 0:
            original_upload_manage = UploadManage.objects.filter(pk=original_upload_manage_id).prefetch_related('file').first()
            original_files = original_upload_manage.file.filter(del_flag=0).all()
            
            for file in original_files:
                file_id = file.id
                filemodel = Filemodel.objects.get(pk=file_id)
                filemodel.id = None
                filemodel.save()

                upload_manage_tmp.file.add(filemodel)

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 2
        
        # 複製データ
        files_tmp = upload_manage_tmp.file.filter(del_flag=0).all()
        files = files_tmp
        context["files"] = files

        upload_manage_tmp = UploadManage.objects.filter(pk=upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()
        file = serializers.serialize("json", files, fields=('name', 'size', 'upload', 'id'))
        context["dist_file"] = file

        # URLを返す
        url_name = self.request.resolver_match.url_name
        context["url_name"] = url_name
        
        return context

    def post(self, request, *args, **kwargs):
        self.del_file = request.POST.getlist('del_file')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        # セッションの対象IDからDBオブジェクトを生成
        upload_manage_id = self.kwargs['pk']
        upload_manage_id_tmp = self.request.session['upload_manage_id']
        upload_manage = UploadManage.objects.get(pk=upload_manage_id)
        upload_manage_tmp = UploadManage.objects.get(pk=upload_manage_id_tmp)

        # 作成日を更新
        upload_manage.created_date = datetime.datetime.now()

        # ファイルの削除
        if 'del_file_pk' in self.request.session:
            del_file_pk = self.request.session['del_file_pk']

            files = Filemodel.objects.filter(pk__in=del_file_pk)
            for file in files:

                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)
                # ファイルパスを分割してファイル名だけ取得
                # file_name = file_path.split('/', 3)[3]
                file_name = file_path.split('/', 2)[2]
                
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
        upload_manage.save()

        if 'up_file_id' in self.request.session:

            # ファイルとタスクを紐付ける
            # ファイル情報をセッションから取得
            up_file_id_str = self.request.session['up_file_id'].replace(" ", "").replace("[", "").replace("]", "")

            # リストに変換
            up_file_id_list = up_file_id_str.split(',')

            # リストのInt型に変換
            up_file_id_int = [int(s) for s in up_file_id_list]

            # オブジェクトの取得
            files = Filemodel.objects.filter(pk__in=up_file_id_int, del_flag=0)
            print("files", files)
            # タスクとファイルを紐付ける
            for file in files:
                upload_manage_tmp.file.add(file)

                t = threading.Thread
                # PDF変換
                # ①ファイル名から拡張子のみ取得
                file_name = file.name

                file_name_without_dot = os.path.splitext(file_name)[1][1:]
                file_name_no_extention = os.path.splitext(file_name)[0]

                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)

                # ファイルパスを分割してファイル名だけ取得
                # file_name = file_path.split('/', 3)[3]
                file_name = file_path.split('/', 2)[2]

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

        # 保存
        upload_manage.save()

        return HttpResponseRedirect(reverse('draganddrop:duplicate_step2', kwargs={'pk': upload_manage_id}))

class DuplicateStep3(TemplateView, CommonView):  # サーバサイドだけの処理
    template_name = 'draganddrop/duplicate/duplicate_step3.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upload_manage_original_id = self.kwargs['pk'] # 複製元データ
        upload_manage_id = self.request.session['upload_manage_id'] # 複製データ

        context["upload_manage_id"] = upload_manage_id
        
        # 複製元データ
        upload_manage_original = UploadManage.objects.filter(pk=upload_manage_original_id).prefetch_related('file').first()
        # 複製データ
        upload_manage = UploadManage.objects.filter(pk=self.request.session['upload_manage_id']).first()
        upload_manage.tmp_flag = 0

        upload_manage.save()

        # 複製元ファイルと複製ファイルを結合
        upload_manage_file = upload_manage_original.file.filter(del_flag=0).all() | upload_manage.file.filter(del_flag=0).all()

        context["upload_manage"] = upload_manage

        # Downloadtableへ保存

        # upload_manageに紐付くグループを取得
        dest_user_groups = upload_manage.dest_user_group.all()
        for group in dest_user_groups:
            for download_user in group.address.all():
                # ユーザー毎のダウンロード状況を管理するテーブルを作成
                downloadtable, created = Downloadtable.objects.get_or_create(upload_manage=upload_manage,dest_user=download_user)
                downloadtable.save()
                # Downloadfiletableへ保存
                for file in upload_manage.file.filter(del_flag=0).all():
                    # ファイル毎のダウンロード状況を管理するテーブルを作成
                    downloadfiletable, created = DownloadFiletable.objects.get_or_create(download_table=downloadtable, download_file=file)
                    downloadfiletable.download_file = file
                    downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        for download_user in upload_manage.dest_user.all():
            # ユーザー毎のダウンロード状況を管理するテーブルを作成
            downloadtable, created = Downloadtable.objects.get_or_create(upload_manage=upload_manage,dest_user=download_user)
            downloadtable.save()
            
            for file in upload_manage.file.filter(del_flag=0).all():
                # ファイル毎のダウンロード状況を管理するテーブルを作成
                downloadfiletable, created = DownloadFiletable.objects.get_or_create(download_table=downloadtable, download_file=file)
                downloadfiletable.download_file = file
                downloadfiletable.save()

        # PersonalResourceManagement,ResourceManagementへ保存
        
        # ログインユーザーが作成したupload_manageを取得
        personal_user_upload_manages = UploadManage.objects.filter(created_user=self.request.user.id).all()
        upload_manage_file_size = 0
        download_table = 0
        download_file_table = 0
        for personal_user_upload_manage in personal_user_upload_manages:

            # ファイルの合計サイズを取得
            for file in personal_user_upload_manage.file.filter(del_flag=0).all():
                upload_manage_file_size = upload_manage_file_size + int(file.size)

            # download_tableのレコード数を取得
            download_table += Downloadtable.objects.filter(upload_manage=personal_user_upload_manage).all().count()

            # download_file_tableのレコード数を取得
            for downloadtable in Downloadtable.objects.filter(upload_manage=personal_user_upload_manage).all():
                download_file_table += int(downloadtable.downloadtable.all().count())

        # 個人管理テーブルの作成・更新
        total_data_usage(upload_manage, self.request.user.company.id, self.request.user.id, download_table, download_file_table, upload_manage_file_size, 1)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)



        # ユーザーの承認ワークフロー設定を取得
        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        # print("------------------ approval_workflow step2", approval_workflow)

        # 承認ワークフローが「使用する」に設定されている場合
        if approval_workflow.is_approval_workflow:

            # 申請ステータスを「申請中」に設定
            upload_manage.application_status = 1
            upload_manage.save()

            # 一次承認者を取得
            first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
            # print("------------------ first_approvers step2", first_approvers)
            # 二次承認者を取得
            second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
            # print("------------------ second_approver step2", second_approvers)

            if first_approvers:
                # print("------------------ first_approversがいます step2")
                for first_approver in first_approvers:
                    # print("------------------ first_approversがいます", first_approver.first_approver)
                    # ApprovalManageを作成
                    first_approver_approval_manage = ApprovalManage.objects.create(
                        upload_manage = upload_manage,
                        manage_id = upload_manage.pk,
                        application_title = upload_manage.title,
                        application_user = upload_manage.created_user,
                        application_date = upload_manage.created_date,
                        application_user_company_id = upload_manage.company,
                        approval_status = 1,
                        first_approver = first_approver.first_approver,
                        upload_method = 1 # 通常アップロード
                    )
                    first_approver_approval_manage.save()

            if second_approvers:
                # print("------------------ second_approversがいます step2")
                for second_approver in second_approvers:
                    # ApprovalManageを作成
                    second_approver_approval_manage = ApprovalManage.objects.create(
                        upload_manage = upload_manage,
                        manage_id = upload_manage.pk,
                        application_title = upload_manage.title,
                        application_user = upload_manage.created_user,
                        application_date = upload_manage.created_date,
                        application_user_company_id = upload_manage.company,
                        approval_status = 1,
                        second_approver = second_approver.second_approver,
                        upload_method = 1 # 通常アップロード
                    )
                    second_approver_approval_manage.save()

        return context


"""
URL 複製
"""
class UrlDuplicateStep1(FormView, CommonView):
    model = UrlUploadManage
    template_name = 'draganddrop/url_duplicate/url_duplicate_step1.html'
    form_class = ManageTasksUrlStep1Form

        # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(UrlDuplicateStep1, self).get_form_kwargs()
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
                        'title': url_upload_manage_old.title + "_copy",
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
        # アップロード方法をセット
        url_upload_manage.upload_method = 2 # URL共有

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

        #URLの作成
        #ランダムな文字列を作る
        def get_random_chars(char_num=Token_LENGTH):
            return "".join([random.choice(string.ascii_letters + string.digits) for i in range(char_num)])

        # アクティベーションURL生成
        Timestamp_signer = TimestampSigner()
        context = {}
        token = get_random_chars()
        url_upload_manage.decode_token = token #tokenをDBに保存
        token_signed = Timestamp_signer.sign(token)  # ランダムURLの生成
        context["token_signed"] = token_signed
        current_site = get_current_site(self.request)
        domain = current_site.domain
        print('domainとは',domain)
        protocol = self.request.scheme        
        url_upload_manage.url = protocol + "://" + domain + "/" + "url_check" + "/" + token_signed

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
        url_upload_manage_id_old = self.kwargs['pk']
        self.request.session['url_upload_manage_id'] = url_upload_manage_id

        # ステップ2へ遷移
        return HttpResponseRedirect(reverse('draganddrop:url_duplicate_step2', kwargs={'pk': url_upload_manage_id_old}))

class UrlDuplicateStep2(FormView, CommonView):
    model = UrlUploadManage
    template_name = "draganddrop/url_duplicate/url_duplicate_step2.html"
    form_class = UrlDistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        original_url_upload_manage_id = self.kwargs['pk'] #複製元データ
        context["url_upload_manage_id"] = original_url_upload_manage_id
        
        url_upload_manage_id_tmp = self.request.session['url_upload_manage_id']
        
        url_upload_manage_tmp = UrlUploadManage.objects.filter(pk=url_upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()
        number_of_files = url_upload_manage_tmp.file.filter(del_flag=0).all().count()
        if number_of_files == 0:
            original_url_upload_manage = UrlUploadManage.objects.filter(pk=original_url_upload_manage_id).prefetch_related('file').first()
            original_files = original_url_upload_manage.file.filter(del_flag=0).all()
            
            for file in original_files:
                file_id = file.id
                filemodel = Filemodel.objects.get(pk=file_id)
                filemodel.id = None
                filemodel.save()

                url_upload_manage_tmp.file.add(filemodel)

        url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["url_upload_manages"] = url_upload_manages

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 2

        
        # 複製データ
        url_upload_manage_tmp = UrlUploadManage.objects.filter(pk=url_upload_manage_id_tmp).prefetch_related('file').first()
        
        files_tmp = url_upload_manage_tmp.file.filter(del_flag=0).all()
        files = files_tmp

        # url_upload_manage = UrlUploadManage.objects.filter(pk=url_upload_manage_id).prefetch_related('file', 'dest_user').first()
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
                # file_name = file_path.split('/', 3)[3]
                file_name = file_path.split('/', 2)[2]
                
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
            files = Filemodel.objects.filter(pk__in=up_file_id_int, del_flag=0)
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
                # file_name = file_path.split('/', 3)[3]
                file_name = file_path.split('/', 2)[2]

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
        
        return HttpResponseRedirect(reverse('draganddrop:url_duplicate_step2', kwargs={'pk': url_upload_manage_id}))

class UrlDuplicateStep3(TemplateView, CommonView):
    template_name = 'draganddrop/url_duplicate/url_duplicate_step3.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        url_upload_manage_original_id = self.kwargs['pk'] # 複製元データ
        url_upload_manage_id = self.request.session['url_upload_manage_id'] # 複製データ

        context["url_upload_manage_id"] = url_upload_manage_id

        # 複製元データ
        url_upload_manage_original = UrlUploadManage.objects.filter(pk=url_upload_manage_original_id).prefetch_related('file').first()
        # 複製データ
        url_upload_manage = UrlUploadManage.objects.filter(pk=self.request.session['url_upload_manage_id']).first()
        url_upload_manage.tmp_flag = 0

        url_upload_manage.save()

        # 複製元ファイルと複製ファイルを結合
        url_upload_manage_file = url_upload_manage_original.file.filter(del_flag=0).all() | url_upload_manage.file.filter(del_flag=0).all()

        context["url_upload_manage"] = url_upload_manage

        # url_upload_manageに紐付くグループを取得
        dest_user_groups = url_upload_manage.dest_user_group.all()
        for group in dest_user_groups:
            for download_user in group.address.all():
                # ユーザー毎のダウンロード状況を管理するテーブルを作成
                url_downloadtable, created = UrlDownloadtable.objects.get_or_create(url_upload_manage=url_upload_manage, dest_user=download_user)
                url_downloadtable.save()
            
                # UrlDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
                for file in url_upload_manage.file.filter(del_flag=0).all():
                    # ファイル毎のダウンロード状況を管理するテーブルを作成
                    url_downloadfiletable, created = UrlDownloadFiletable.objects.get_or_create(url_download_table=url_downloadtable, download_file=file)
                    url_downloadfiletable.download_file = file
                    url_downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        for download_user in url_upload_manage.dest_user.all():
            url_downloadtable, created = UrlDownloadtable.objects.get_or_create(url_upload_manage=url_upload_manage, dest_user=download_user)
            url_downloadtable.save()

            # UrlDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
            for file in url_upload_manage.file.filter(del_flag=0).all():
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

        # 個人管理テーブルの作成・更新
        total_data_usage(url_upload_manage, self.request.user.company.id, self.request.user.id, download_table, download_file_table, url_upload_manage_file_size, 2)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)


        # ユーザーの承認ワークフロー設定を取得
        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        # print("------------------ approval_workflow step2", approval_workflow)

        # 承認ワークフローが「使用する」に設定されている場合
        if approval_workflow.is_approval_workflow:

            # 申請ステータスを「申請中」に設定
            url_upload_manage.application_status = 1
            url_upload_manage.save()

            # 一次承認者を取得
            first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
            # print("------------------ first_approvers step2", first_approvers)
            # 二次承認者を取得
            second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
            # print("------------------ second_approver step2", second_approvers)

            if first_approvers:
                # print("------------------ first_approversがいます step2")
                for first_approver in first_approvers:
                    # print("------------------ first_approversがいます", first_approver.first_approver)
                    # ApprovalManageを作成
                    first_approver_approval_manage = ApprovalManage.objects.create(
                        url_upload_manage = url_upload_manage,
                        manage_id = url_upload_manage.pk,
                        application_title = url_upload_manage.title,
                        application_user = url_upload_manage.created_user,
                        application_date = url_upload_manage.created_date,
                        application_user_company_id = url_upload_manage.company,
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
                        url_upload_manage = url_upload_manage,
                        manage_id = url_upload_manage.pk,
                        application_title = url_upload_manage.title,
                        application_user = url_upload_manage.created_user,
                        application_date = url_upload_manage.created_date,
                        application_user_company_id = url_upload_manage.company,
                        approval_status = 1,
                        second_approver = second_approver.second_approver,
                        upload_method = 2 # URL共有
                    )
                    second_approver_approval_manage.save()

        return context

"""
OTP 複製
"""
class OTPDuplicateStep1(FormView, CommonView):
    model = OTPUploadManage
    template_name = 'draganddrop/otp_duplicate/otp_duplicate_step1.html'
    form_class = ManageTasksOTPStep1Form

        # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(OTPDuplicateStep1, self).get_form_kwargs()
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
            dl_limit = otp_upload_manage.dl_limit
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
                        'dl_limit': dl_limit,
                        'end_date': end_date,
                        'message': message
                    }

        # formに新たな値が書き込まれなかった時に元の旧データを返す処理。
        else:
            otp_upload_manage_old = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
            initial = {
                        'title': otp_upload_manage_old.title + "_copy",
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
                        'dl_limit': otp_upload_manage_old.dl_limit,
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
        dl_limit = form.cleaned_data['dl_limit']
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
        # ダウンロード回数をセット
        otp_upload_manage.dl_limit = dl_limit
        # メッセージをセット
        otp_upload_manage.message = message
        # アップロード方法をセット
        otp_upload_manage.upload_method = 3 # 通常アップロード

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

        #URLの作成
        #ランダムな文字列を作る
        def get_random_chars(char_num=Token_LENGTH):
            return "".join([random.choice(string.ascii_letters + string.digits) for i in range(char_num)])

        # アクティベーションURL生成
        Timestamp_signer = TimestampSigner()
        context = {}
        token = get_random_chars()
        otp_upload_manage.decode_token = token #tokenをDBに保存
        token_signed = Timestamp_signer.sign(token)  # ランダムURLの生成
        context["token_signed"] = token_signed
        current_site = get_current_site(self.request)
        domain = current_site.domain
        print('domainとは',domain)
        protocol = self.request.scheme        
        otp_upload_manage.url = protocol + "://" + domain + "/" + "otp_check" + "/" + token_signed

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
        self.request.session['dl_limit'] = dl_limit
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
        otp_upload_manage_id_old = self.kwargs['pk']
        self.request.session['otp_upload_manage_id'] = otp_upload_manage_id

        # ステップ2へ遷移
        return HttpResponseRedirect(reverse('draganddrop:otp_duplicate_step2', kwargs={'pk': otp_upload_manage_id_old}))

class OTPDuplicateStep2(FormView, CommonView):
    model = OTPUploadManage
    template_name = "draganddrop/otp_duplicate/otp_duplicate_step2.html"
    form_class = OTPDistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        original_otp_upload_manage_id = self.kwargs['pk'] #複製元データ
        context["otp_upload_manage_id"] = original_otp_upload_manage_id
        
        otp_upload_manage_id_tmp = self.request.session['otp_upload_manage_id']
        
        otp_upload_manage_tmp = OTPUploadManage.objects.filter(pk=otp_upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()
        number_of_files = otp_upload_manage_tmp.file.filter(del_flag=0).all().count()
        if number_of_files == 0:
            original_otp_upload_manage = OTPUploadManage.objects.filter(pk=original_otp_upload_manage_id).prefetch_related('file').first()
            original_files = original_otp_upload_manage.file.filter(del_flag=0).all()
            
            for file in original_files:
                file_id = file.id
                filemodel = Filemodel.objects.get(pk=file_id)
                filemodel.id = None
                filemodel.save()

                otp_upload_manage_tmp.file.add(filemodel)

        otp_upload_manages = OTPUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["otp_upload_manages"] = otp_upload_manages

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 2

        
        # 複製データ
        otp_upload_manage_tmp = OTPUploadManage.objects.filter(pk=otp_upload_manage_id_tmp).prefetch_related('file').first()
        
        files_tmp = otp_upload_manage_tmp.file.filter(del_flag=0).all()
        files = files_tmp

        # otp_upload_manage = OTPUploadManage.objects.filter(pk=otp_upload_manage_id).prefetch_related('file', 'dest_user').first()
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

            files = OTPFilemodel.objects.filter(pk__in=del_file_pk)

            for file in files:
                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)
                # ファイルパスを分割してファイル名だけ取得
                # file_name = file_path.split('/', 3)[3]
                file_name = file_path.split('/', 2)[2]
                
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
            files = Filemodel.objects.filter(pk__in=up_file_id_int, del_flag=0)
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
                # file_name = file_path.split('/', 3)[3]
                file_name = file_path.split('/', 2)[2]

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
        
        return HttpResponseRedirect(reverse('draganddrop:otp_duplicate_step2', kwargs={'pk': otp_upload_manage_id}))

class OTPDuplicateStep3(TemplateView, CommonView):
    template_name = 'draganddrop/otp_duplicate/otp_duplicate_step3.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        otp_upload_manage_original_id = self.kwargs['pk'] # 複製元データ
        otp_upload_manage_id = self.request.session['otp_upload_manage_id'] # 複製データ

        context["otp_upload_manage_id"] = otp_upload_manage_id

        # 複製元データ
        otp_upload_manage_original = OTPUploadManage.objects.filter(pk=otp_upload_manage_original_id).prefetch_related('file').first()
        # 複製データ
        otp_upload_manage = OTPUploadManage.objects.filter(pk=self.request.session['otp_upload_manage_id']).first()
        otp_upload_manage.tmp_flag = 0

        otp_upload_manage.save()

        # 複製元ファイルと複製ファイルを結合
        otp_upload_manage_file = otp_upload_manage_original.file.filter(del_flag=0).all() | otp_upload_manage.file.filter(del_flag=0).all()

        context["otp_upload_manage"] = otp_upload_manage

        # otp_upload_manageに紐付くグループを取得
        dest_user_groups = otp_upload_manage.dest_user_group.all()
        for group in dest_user_groups:
            for download_user in group.address.all():
                # ユーザー毎のダウンロード状況を管理するテーブルを作成
                otp_downloadtable, created = OTPDownloadtable.objects.get_or_create(otp_upload_manage=otp_upload_manage, dest_user=download_user)
                otp_downloadtable.save()
            
                # OTPDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
                for file in otp_upload_manage.file.filter(del_flag=0).all():
                    # ファイル毎のダウンロード状況を管理するテーブルを作成
                    otp_downloadfiletable, created = OTPDownloadFiletable.objects.get_or_create(otp_download_table=otp_downloadtable, download_file=file)
                    otp_downloadfiletable.download_file = file
                    otp_downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        for download_user in otp_upload_manage.dest_user.all():
            otp_downloadtable, created = OTPDownloadtable.objects.get_or_create(otp_upload_manage=otp_upload_manage, dest_user=download_user)
            otp_downloadtable.save()

            # OTPDownloadfiletableへ保存(ファイル毎のダウンロード状況を管理するテーブルを作成)
            for file in otp_upload_manage.file.filter(del_flag=0).all():
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
        total_data_usage(otp_upload_manage, self.request.user.company.id, self.request.user.id, download_table, download_file_table, otp_upload_manage_file_size, 3)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)


        # ユーザーの承認ワークフロー設定を取得
        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        # print("------------------ approval_workflow step2", approval_workflow)

        # 承認ワークフローが「使用する」に設定されている場合
        if approval_workflow.is_approval_workflow:

            # 申請ステータスを「申請中」に設定
            otp_upload_manage.application_status = 1
            otp_upload_manage.save()

            # 一次承認者を取得
            first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
            # print("------------------ first_approvers step2", first_approvers)
            # 二次承認者を取得
            second_approvers = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
            # print("------------------ second_approver step2", second_approvers)

            if first_approvers:
                # print("------------------ first_approversがいます step2")
                for first_approver in first_approvers:
                    # print("------------------ first_approversがいます", first_approver.first_approver)
                    # ApprovalManageを作成
                    first_approver_approval_manage = ApprovalManage.objects.create(
                        otp_upload_manage = otp_upload_manage,
                        manage_id = otp_upload_manage.pk,
                        application_title = otp_upload_manage.title,
                        application_user = otp_upload_manage.created_user,
                        application_date = otp_upload_manage.created_date,
                        application_user_company_id = otp_upload_manage.company,
                        approval_status = 1,
                        first_approver = first_approver.first_approver,
                        upload_method = 3 # OTP共有
                    )
                    first_approver_approval_manage.save()

            if second_approvers:
                # print("------------------ second_approversがいます step2")
                for second_approver in second_approvers:
                    # ApprovalManageを作成
                    second_approver_approval_manage = ApprovalManage.objects.create(
                        otp_upload_manage = otp_upload_manage,
                        manage_id = otp_upload_manage.pk,
                        application_title = otp_upload_manage.title,
                        application_user = otp_upload_manage.created_user,
                        application_date = otp_upload_manage.created_date,
                        application_user_company_id = otp_upload_manage.company,
                        approval_status = 1,
                        second_approver = second_approver.second_approver,
                        upload_method = 3 # OTP共有
                    )
                    second_approver_approval_manage.save()



        return context

###########################
# 複製 戻る  #
###########################
"""
アップロード用
"""
class DuplicateReturnView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        upload_manage_id = self.kwargs['pk']

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:duplicate_step1', kwargs={'pk': upload_manage_id}))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:duplicate_step1', kwargs={'pk': upload_manage_id}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:duplicate_step2', kwargs={'pk': upload_manage_id}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:duplicate_step3', kwargs={'pk': upload_manage_id}))

"""
URL用
"""
class UrlDuplicateReturnView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        url_upload_manage_id = self.kwargs['pk']

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:url_duplicate_step1', kwargs={'pk': url_upload_manage_id}))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:url_duplicate_step1', kwargs={'pk': url_upload_manage_id}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:url_duplicate_step2', kwargs={'pk': url_upload_manage_id}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:url_duplicate_step3', kwargs={'pk': url_upload_manage_id}))
"""
OTP用
"""
class OTPDuplicateReturnView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        otp_upload_manage_id = self.kwargs['pk']

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:otp_duplicate_step1', kwargs={'pk': otp_upload_manage_id}))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:otp_duplicate_step1', kwargs={'pk': otp_upload_manage_id}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:otp_duplicate_step2', kwargs={'pk': otp_upload_manage_id}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:otp_duplicate_step3', kwargs={'pk': otp_upload_manage_id}))
