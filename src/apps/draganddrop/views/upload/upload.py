from django.shortcuts import render
from django.views.generic import FormView, View, CreateView, TemplateView
from draganddrop.views.home.home_common import CommonView, total_data_usage, resource_management_calculation_process
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import ManageTasksStep1Form, DistFileUploadForm
from draganddrop.models import UploadManage, PDFfilemodel, Address, Group, Filemodel, Downloadtable, DownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation, ApprovalOperationLog, ApprovalManage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core import serializers
import datetime
import urllib.parse
import os
from django.conf import settings
import threading

###########################
# アップロード機能  #
###########################

class Step1(FormView, CommonView):
    model = UploadManage
    template_name = 'draganddrop/upload/step1_update.html'
    form_class = ManageTasksStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(Step1, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'url': self.request.resolver_match.url_name})
        return kwargs


    # 戻るを実装した際に最初に入力した値を表示するための処理。formに使用する初期データを返す。
    def get_initial(self):

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 1

        # if文で適宜しないと一番最初のアップロード時エラーが出る。セッションにデータがある場合この処理をするという意味。
        if 'upload_manage_id' in self.request.session:
            upload_manage_id = self.request.session['upload_manage_id']
            upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user').first()

            initial = {
                'title': upload_manage.title,
                'dest_user': upload_manage.dest_user.all(),
                'dest_user_group': upload_manage.dest_user_group.all(),
                'dest_user_mail1': upload_manage.dest_user_mail1,
                'dest_user_mail2': upload_manage.dest_user_mail2,
                'dest_user_mail3': upload_manage.dest_user_mail3,
                'dest_user_mail4': upload_manage.dest_user_mail4,
                'dest_user_mail5': upload_manage.dest_user_mail5,
                'dest_user_mail6': upload_manage.dest_user_mail6,
                'dest_user_mail7': upload_manage.dest_user_mail7,
                'dest_user_mail8': upload_manage.dest_user_mail8,
                'end_date': upload_manage.end_date,
                'message': upload_manage.message,
                'dl_limit': str(upload_manage.dl_limit),
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
        if 'upload_manage_id' in self.request.session:
            # セッションに存在するテンポラリオブジェクトモデルのIDを取得
            upload_manage_id = self.request.session['upload_manage_id']

            # モデルオブジェクトを取得
            upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user').first()

            #context["dest_users"] = upload_manage.dest_user.all()
            # アドレス帳の選択済みユーザー一覧をテンプレートへ渡す
            pk_list = upload_manage.dest_user.all().values_list('pk', flat=True)
            context["pk_list"] = list(pk_list)
            
            group_list = upload_manage.dest_user_group.all().values_list('pk', flat=True)
            context["group_list"] = list(group_list)

        return context


    # データがポストされた時に呼ばれるメソッド
    def form_valid(self, form):

        # ★セッション中に「upload_manage_id」というセッション情報があるか判断する。
        if 'upload_manage_id' in self.request.session:
            upload_manage = UploadManage.objects.filter(pk=self.request.session['upload_manage_id']).first()

        else:
            # フォームからDBのオブジェクトを仮生成（未保存）
            upload_manage = form.save(commit=False)

        # ログインユーザーを登録者としてセット
        upload_manage.created_user = self.request.user.id
        # ログインユーザーの会社idをセット
        upload_manage.company = self.request.user.company.id
        # 作成日をセット
        upload_manage.created_date = datetime.datetime.now()
        # テンポラリフラグをセット(既に作成済みか、作成途中か判断するため)
        upload_manage.tmp_flag = 1

        #入力されたデータを取得してDBに保存
        # タイトルを取得
        title = form.cleaned_data['title']
        upload_manage.title = title
        # 保存期日を取得
        end_date = form.cleaned_data['end_date']
        upload_manage.end_date = end_date
        # ダウンロード回数を取得
        dl_limit = form.cleaned_data['dl_limit']
        upload_manage.dl_limit = dl_limit
        # メッセージ取得
        message = form.cleaned_data['message']
        upload_manage.message = message

        # 保存
        upload_manage.save()

        # メールアドレス直接入力DBへ保存
        dest_user_mail1 = form.cleaned_data['dest_user_mail1']

        # TODO:直接入力をADRESSに登録する必要あるか？
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

        # upload_manageに追加する。（データを追加し、戻った際にデータを反映させるため）
        upload_manage.dest_user_mail1 = dest_user_mail1
        upload_manage.dest_user_mail2 = dest_user_mail2
        upload_manage.dest_user_mail3 = dest_user_mail3
        upload_manage.dest_user_mail4 = dest_user_mail4
        upload_manage.dest_user_mail5 = dest_user_mail5
        upload_manage.dest_user_mail6 = dest_user_mail6
        upload_manage.dest_user_mail7 = dest_user_mail7
        upload_manage.dest_user_mail8 = dest_user_mail8

        # POSTで送信された設定された宛先ユーザーを取得
        dest_user_qs = form.cleaned_data['dest_user']
        # MonyToMonyの値はquerysetとして取得するので、set関数を使ってセット
        upload_manage.dest_user.set(dest_user_qs)

        dest_user_group_qs = form.cleaned_data['dest_user_group']
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
        self.request.session['end_date'] = end_date
        self.request.session['dl_limit'] = dl_limit
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
        upload_manage.save()
        upload_manage_id = str(upload_manage.id)

        # 生成されたDBの対象行のIDをセッションに保存しておく
        self.request.session['upload_manage_id'] = upload_manage_id

        # ステップ2へ遷移(ファイルを選択するステップ)
        return HttpResponseRedirect(reverse('draganddrop:step2', kwargs={'pk': upload_manage_id}))

class Step2(LoginRequiredMixin, CreateView, CommonView):
    model = UploadManage
    template_name = "draganddrop/upload/step2_update.html"
    form_class = DistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upload_manage_id = self.kwargs['pk']
        context["upload_manage_id"] = upload_manage_id
        upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('file').first()
        files = upload_manage.file.all()
        context["files"] = files

        files = serializers.serialize("json", files, fields=('name', 'size', 'upload', 'id'))
        context["dist_file"] = files
        # 削除IDを取得
        if 'del_file_pk' in self.request.session:
            context["del_file_pk"] = self.request.session['del_file_pk']
        else:
            context["del_file_pk"] = None
        
        return context

    def post(self, request, *args, **kwargs):
        self.del_file = request.POST.getlist('del_file')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print('updalods_2のform_valid')
        upload_manage_id = self.kwargs['pk']
        upload_manage = UploadManage.objects.filter(pk=upload_manage_id).first()

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

                upload_manage.file.add(file)

                t = threading.Thread
                # PDF変換
                # ①ファイル名から拡張子のみ取得
                file_name = file.name

                file_name_without_dot = os.path.splitext(file_name)[1][1:]
                file_name_no_extention = os.path.splitext(file_name)[0]

                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(file.upload.url)
                print('ふぁいるぱす',file_path)
                # ファイルパスを分割してファイル名だけ取得
                # file_name = file_path.split('/', 2)[2]
                file_name = file_path.split('/', 3)[3]
                print('ふぁいるめい',file_name)
                # パスを取得
                path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                print('----pathはなに',path)

                # .txtファイルをHTMLファイルへ変換
                # テキストファイルを一括で読み込む
                if file_name_without_dot == "txt":
                    path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                    with open(path) as f:
                        s = f.read()

                        # htmlファイルを生成して書き込む
                        upload_s = str(file.upload)
                        print('----------uplod_sとは',upload_s)
                        upload_ss = upload_s.split('/')[0]
                        print('----------uplod_ssとは',upload_ss)

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
                        print('path_html_s部分',path_html_s)
                        htmlfile, created = PDFfilemodel.objects.get_or_create(
                            name=htmlname,
                            size=file.size,
                            upload=path_html_s,
                            file=file
                        )

                        htmlfile.save()

        upload_manage.save()

        print("------------------- Step2")

        return HttpResponseRedirect(reverse('draganddrop:step2', kwargs={'pk': upload_manage.id}))

class Step3(TemplateView, CommonView):
    template_name = 'draganddrop/upload/step3_update.html'

    def get_context_data(self, **kwargs):

        print("------------------- Step3")

        context = super().get_context_data(**kwargs)

        upload_manage_id = self.kwargs['pk']

        context["upload_manage_id"] = upload_manage_id

        upload_manage = UploadManage.objects.filter(pk=upload_manage_id).first()
        upload_manage.tmp_flag = 0

        upload_manage.save()

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
                for file in upload_manage.file.all():
                    # ファイル毎のダウンロード状況を管理するテーブルを作成
                    downloadfiletable, created = DownloadFiletable.objects.get_or_create(download_table=downloadtable, download_file=file)
                    downloadfiletable.download_file = file
                    downloadfiletable.save()

        # upload_manageに紐付くdest_userを取得
        for download_user in upload_manage.dest_user.all():
            # ユーザー毎のダウンロード状況を管理するテーブルを作成
            downloadtable, created = Downloadtable.objects.get_or_create(upload_manage=upload_manage,dest_user=download_user)
            downloadtable.save()
            
            for file in upload_manage.file.all():
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
            for file in personal_user_upload_manage.file.all():
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
        # approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()
        # print("------------------ approval_workflow step2", approval_workflow)

        # # 承認ワークフローが「使用する」に設定されている場合
        # if approval_workflow.is_approval_workflow:
        #     # 一次承認者を取得
        #     first_approvers = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id)
        #     print("------------------ first_approvers step2", first_approvers)
        #     # 二次承認者を取得
        #     second_approver = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id)
        #     print("------------------ second_approver step2", second_approver)

        return context

###########################
# アップロード 戻る  #
###########################

class ReturnView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        upload_manage_id = self.kwargs['pk']

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:step1'))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:step1'))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:step2', kwargs={'pk': upload_manage_id}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:step3', kwargs={'pk': upload_manage_id}))


###########################
# アップデート機能  #
###########################

class Step1Update(FormView, CommonView):
    model = UploadManage
    template_name = 'draganddrop/upload/step1_update.html'
    form_class = ManageTasksStep1Form

    # フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(Step1Update, self).get_form_kwargs()
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
                message = upload_manage_old.message
            else:
                message = upload_manage.message

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
                        'message': message,
                        }

        # formに新たな値が書き込まれなかった時に元の旧データを返す処理。
        else:
            upload_manage_old = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('dest_user',).first()  # 旧データ
            initial = {'title': upload_manage_old.title,
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
                        'message': upload_manage_old.message,
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
        return HttpResponseRedirect(reverse('draganddrop:step2_update', kwargs={'pk': upload_manage_id_old}))

class Step2Update(FormView, CommonView):
    model = UploadManage
    template_name = "draganddrop/upload/step2_update.html"
    form_class = DistFileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upload_manage_id = self.kwargs['pk']
        context["upload_manage_id"] = upload_manage_id
        upload_manages = UploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["upload_manages"] = upload_manages

        # ページ情報をセッションに保存しておく
        self.request.session['page_num'] = 2

        upload_manage_id_tmp = self.request.session['upload_manage_id']

        upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('file').first()
        files = upload_manage.file.all()
        upload_manage_tmp = UploadManage.objects.filter(pk=upload_manage_id_tmp).prefetch_related('file').first()

        files_tmp = upload_manage_tmp.file.all()

        files = files | files_tmp
        upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('file', 'dest_user').first()
        upload_manage_tmp = UploadManage.objects.filter(pk=upload_manage_id_tmp).prefetch_related('file', 'dest_user').first()

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
        upload_manage_id = self.kwargs['pk']
        upload_manage_id_tmp = self.request.session['upload_manage_id']
        upload_manage = UploadManage.objects.get(pk=upload_manage_id)
        upload_manage_tmp = UploadManage.objects.get(pk=upload_manage_id_tmp)

        # 作成日を更新
        upload_manage.created_date = datetime.datetime.now()

        # ファイルの削除
        if 'del_file_pk' in self.request.session:
            print('del_file_pkにきた')
            del_file_pk = self.request.session['del_file_pk']

            files = Filemodel.objects.filter(pk__in=del_file_pk)
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
            files = Filemodel.objects.filter(pk__in=up_file_id_int)
            print("編集files", files)
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

        # 保存
        upload_manage.save()


        return HttpResponseRedirect(reverse('draganddrop:step2_update', kwargs={'pk': upload_manage_id}))

class Step3Update(TemplateView, CommonView):  # サーバサイドだけの処理
    template_name = 'draganddrop/upload/step3_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upload_manage_id = self.kwargs['pk']
        upload_manage_id_tmp = self.request.session['upload_manage_id']

        upload_manage = UploadManage.objects.filter(pk=upload_manage_id).prefetch_related('file').first()
        upload_manage_tmp = UploadManage.objects.filter(pk=upload_manage_id_tmp).prefetch_related('file').first()

        # 旧download_tableの取得(新に変更される前に)
        number_of_download_table_old =  Downloadtable.objects.filter(upload_manage=upload_manage).all().count()

        # 旧download_file_tableの取得
        number_of_download_file_table_old = 0
        for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
            number_of_download_file_table_old += int(downloadtable.downloadtable.all().count())
        # 旧ファイルの合計サイズ
        upload_manage_file_size_old = 0
        for file in upload_manage.file.all():
            upload_manage_file_size_old = upload_manage_file_size_old + int(file.size)
     
        #削除対象の送信先を取得・削除

        # アドレス帳から選択したユーザーと直接入力
        dest_user = upload_manage.dest_user.all() #旧データ
        dest_user_tmp = upload_manage_tmp.dest_user.all() #新データ
        delete_dest_users=set(dest_user).difference(set(dest_user_tmp)) #差分の値を取得(新データには含まれていない送信先を特定する)
        for delete_dest_user in delete_dest_users: #set型の要素を個別に取り出す
            downloadtable = Downloadtable.objects.filter(upload_manage=upload_manage, dest_user=delete_dest_user.id) #削除対象の値を取得
            downloadtable.delete()
        
        #グループ
        dest_user_group = upload_manage.dest_user_group.all() #旧データ
        dest_user_group_tmp = upload_manage_tmp.dest_user_group.all() #新データ
        delete_dest_user_groups=set(dest_user_group).difference(set(dest_user_group_tmp)) #差分の値を取得(新データには含まれていない送信先を特定する)
        for group in delete_dest_user_groups: #set型の要素を個別に取り出す
            for delete_dest_user_group in group.address.all():
                downloadtable = Downloadtable.objects.filter(upload_manage=upload_manage, dest_user=delete_dest_user_group.id) #削除対象の値を取得
                downloadtable.delete()

        #更新データをUploadManageに保存
        upload_manage.title = upload_manage_tmp.title
        upload_manage.end_date = upload_manage_tmp.end_date
        upload_manage.dl_limit = upload_manage_tmp.dl_limit
        upload_manage.message = upload_manage_tmp.message
        upload_manage.dest_user_mail1 = upload_manage_tmp.dest_user_mail1
        upload_manage.dest_user_mail2 = upload_manage_tmp.dest_user_mail2
        upload_manage.dest_user_mail3 = upload_manage_tmp.dest_user_mail3
        upload_manage.dest_user_mail4 = upload_manage_tmp.dest_user_mail4
        upload_manage.dest_user_mail5 = upload_manage_tmp.dest_user_mail5
        upload_manage.dest_user_mail6 = upload_manage_tmp.dest_user_mail6
        upload_manage.dest_user_mail7 = upload_manage_tmp.dest_user_mail7
        upload_manage.dest_user_mail8 = upload_manage_tmp.dest_user_mail8

        upload_manage.save()
        
        # 既存ファイルと新ファイルを結合
        upload_manage_file = upload_manage.file.all() | upload_manage_tmp.file.all()

        #Downloadtableへ保存

        # グループに紐付くdownloadtableの作成
        dest_user_groups = upload_manage_tmp.dest_user_group.all()
        for dest_user_group in dest_user_groups:
            for download_user in dest_user_group.address.all():
                downloadtable, created = Downloadtable.objects.get_or_create(upload_manage=upload_manage, dest_user=download_user)
                downloadtable.save()

                # Downloadfiletableへ保存
                for file in upload_manage_file.all():
                    downloadfiletable, created = DownloadFiletable.objects.get_or_create(download_table=downloadtable,download_file = file )
                    downloadfiletable.save()
        
        # アドレス帳から選択したユーザーと直接入力に紐付くdownloadtableの作成
        for download_user in upload_manage_tmp.dest_user.all():
            downloadtable, created = Downloadtable.objects.get_or_create(upload_manage=upload_manage, dest_user=download_user)
            downloadtable.save()

            # Downloadfiletableへ保存
            for file in upload_manage_file.all():
                downloadfiletable, created = DownloadFiletable.objects.get_or_create(download_table=downloadtable,download_file = file )
                downloadfiletable.save()

        
        downloadfiletables = DownloadFiletable.objects.filter(download_table=downloadtable).count()
        downloadfiletables_true = DownloadFiletable.objects.filter(
            download_table=downloadtable, is_downloaded=True).count()
        
        if downloadfiletables == downloadfiletables_true:
            downloadtable.is_downloaded = True
            downloadtable.save()

        else:
            downloadtable.is_downloaded = False
            downloadtable.save()

        file_number = Downloadtable.objects.filter(upload_manage=downloadtable.upload_manage).count()
        downloaded_file_number = Downloadtable.objects.filter(upload_manage=downloadtable.upload_manage, is_downloaded=True).count()

        if file_number == downloaded_file_number:
            upload_manage = downloadtable.upload_manage
            upload_manage.is_downloaded = True  # 対応完了
            upload_manage.save()

        else:
            upload_manage = downloadtable.upload_manage
            upload_manage.is_downloaded = False
            upload_manage.save()

        downloadtable.save()

        for file in upload_manage_tmp.file.all():
            upload_manage.file.add(file)

        upload_manage.save()

        upload_manage.dest_user_group.set(upload_manage_tmp.dest_user_group.all())
        upload_manage.dest_user.set(upload_manage_tmp.dest_user.all())

        # PersonalResourceManagement更新処理
        personal_resource_manage = PersonalResourceManagement.objects.filter(user=self.request.user.id).first()
        # download_tableのレコード数を更新
        number_of_download_table_tmp =  Downloadtable.objects.filter(upload_manage=upload_manage).all().count()
        personal_resource_manage.number_of_download_table += (number_of_download_table_tmp - number_of_download_table_old)
        
        # 新ファイルの合計サイズ
        upload_manage_file_size = 0
        for file in upload_manage.file.all():
            upload_manage_file_size = upload_manage_file_size + int(file.size)
        personal_resource_manage.upload_manage_file_size += (upload_manage_file_size - upload_manage_file_size_old)

        # download_file_tableのレコード数を更新
        number_of_download_file_table_tmp = 0
        for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
            number_of_download_file_table_tmp += int(downloadtable.downloadtable.all().count())
        personal_resource_manage.number_of_download_file_table += (number_of_download_file_table_tmp - number_of_download_file_table_old)
        personal_resource_manage.save()
        
        # tmpレコード削除
        tmp_flag_1 = UploadManage.objects.filter(tmp_flag=1).all()
        tmp_flag_1.delete()

        download_table = personal_resource_manage.number_of_download_table
        download_file_table = personal_resource_manage.number_of_download_file_table
        total_file_size = personal_resource_manage.total_file_size
        
        # 個人管理テーブルの作成・更新
        total_data_usage(upload_manage, self.request.user.company.id, self.request.user.id, download_table, download_file_table, upload_manage_file_size, 1)
        # 会社管理テーブルの作成・更新
        resource_management_calculation_process(self.request.user.company.id)

        return context

###########################
# アップデート 戻る  #
###########################

class ReturnUpdateView(View):
    def get(self, request, *args, **kwargs):

        # 不正な遷移をチェック
        if not 'page_num' in self.request.session:
            raise PermissionDenied

        page_num = self.request.session['page_num']

        upload_manage_id_old = self.kwargs['pk']  # 旧データ

        # 2ページから1ページに戻る時の処理
        if page_num == 1:
            return HttpResponseRedirect(reverse('draganddrop:step1_update', kwargs={'pk': upload_manage_id_old}))

        # 3ページから2ページに戻る時の処理
        if page_num == 2:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 1
            return HttpResponseRedirect(reverse('draganddrop:step1_update', kwargs={'pk': upload_manage_id_old}))

        # 4ページから3ページに戻る時の処理
        if page_num == 3:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 2
            return HttpResponseRedirect(reverse('draganddrop:step2_update', kwargs={'pk': upload_manage_id_old}))

        # 5ページから4ページに戻る時の処理
        if page_num == 4:
            # ページ情報をセッションに保存しておく
            self.request.session['page_num'] = 3
            return HttpResponseRedirect(reverse('draganddrop:step3_update', kwargs={'pk': upload_manage_id_old}))
