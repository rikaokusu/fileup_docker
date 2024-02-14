from django.http import HttpResponse
from django.views.generic import View,ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import ContextMixin
from ...forms import ManageTasksStep1Form
from draganddrop.models import UploadManage, Downloadtable, UrlUploadManage, UrlDownloadtable, OTPUploadManage, OTPDownloadtable, GuestUploadManage, GuestUploadDownloadtable, GuestUploadDownloadFiletable, ResourceManagement, PersonalResourceManagement
from accounts.models import User, File
from draganddrop.models import ApprovalWorkflow, FirstApproverRelation, SecondApproverRelation
from accounts.models import User, File,Notification,Read
from draganddrop.models import ApprovalWorkflow
from draganddrop.forms import UserChangeForm
# from datetime import datetime, date, timedelta, timezone
import datetime
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
import math
from django.shortcuts import redirect, render
from django.http import JsonResponse

# Token_LENGTH = 5  # ランダムURLを作成するためのTOKEN

class CommonView(ContextMixin):

    # ログインユーザーを返す
    def get_context_data(self, **kwargs):
        today = datetime.datetime.now()
        context = super().get_context_data(**kwargs)
        current_user = User.objects.filter(pk=self.request.user.id).select_related().get()
        context["current_user"] = current_user

        url_name = self.request.resolver_match.url_name
        app_name = self.request.resolver_match.app_name

        context["url_name"] = url_name
        context["app_name"] = app_name
        context["current_user"] = current_user

        ######################　通知機能
        my_email = current_user.email

        all_info = Notification.objects.filter(start_date__lte = today)
        #全てのサービスかFileUPの通知のみ取得
        all_info = all_info.filter(
        Q(service="FileUP!") | 
        Q(service="全てのサービス")).order_by('release_date').reverse()
        all_informations = []
        maintenance_informations = []
        notice_informations = []

        for info in all_info:
            info_email = info.email_list
            email_if = my_email in info_email  #True False　自分が通知対象者か
            info_category = info.category
            if email_if == True:
                all_informations.append(info)
                if "メンテナンス" in info_category:
                    maintenance_informations.append(info)
                else: #お知らせ、メッセージ
                    notice_informations.append(info)

        #通知カウントも修正する
        read = Read.objects.filter(read_user=current_user).count()
        read_info = Read.objects.filter(read_user=current_user).values_list('notification_id', flat=True)
        if read > 0:
            no_read = len(all_informations) - read
        else:
            print('通知のかずーーー',len(all_informations))
            no_read = len(all_informations)

        if no_read > 99 :
            context["no_read"] = "99+"

        else:
            context["no_read"] = no_read
        #通知機能おわり
            
        # #インフォメーション
        # all_informations = Notification.objects.filter(start_date__lte = today)
        # notice_informations = Notification.objects.filter(Q(target_user_id = None)|Q(target_user_id = current_user),Q(category = 'メッセージ')|Q(category = 'お知らせ'),start_date__lte = today).distinct().values()
        # maintenance_informations = Notification.objects.filter(Q(target_user_id = None)|Q(target_user_id = current_user),start_date__lte = today, category__contains = 'メンテナンス').distinct().values()
        # read = Read.objects.filter(read_user=current_user).count()
        # read_info = Read.objects.filter(read_user=current_user).values_list('notification_id', flat=True)
        # if read > 0:
        #     info_all = Notification.objects.filter(Q(target_user_id = None)|Q(target_user_id = current_user),start_date__lte = today).distinct().count()
        #     no_read = info_all - read
        # else:
        #     no_read = Notification.objects.filter(Q(target_user_id = None)|Q(target_user_id = current_user),start_date__lte = today).distinct().count()

        # if no_read > 99 :
        #     context["no_read"] = "99+"

        # else:
        #     context["no_read"] = no_read

        email_list = current_user.email.rsplit('@', 1)
        # メールアドレスをユーザ名とドメインに分割
        email_domain = email_list[1]

        url_name = self.request.resolver_match.url_name
        app_name = self.request.resolver_match.app_name

        context["read_info"] = read_info
        context["url_name"] = url_name
        context["app_name"] = app_name
        context["all_informations"] = all_informations
        context["maintenance_informations"] = maintenance_informations
        context["notice_informations"] = notice_informations

        context["current_user"] = current_user
        context["email_domain"] = email_domain
        # information終わり
        
        # 契約プラン
        plan = "light"
        context["plan"] = plan
        
        # 会社毎のファイル合計サイズ
        if ResourceManagement.objects.exists():
            resource_manage = ResourceManagement.objects.filter(company = self.request.user.company.id).first()
            if resource_manage:
                context["total_file_size"] = resource_manage.total_file_size
                # context["total_data_usage"] = resource_manage.total_data_usage
        
        return context

"""
お知らせページ
"""
class InfomationView(LoginRequiredMixin, TemplateView,CommonView):
    template_name = 'accounts/infomation.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        print('インフォメーションがうごいた')
        context = super().get_context_data(**kwargs)
        user = self.request.user
        info = Notification.objects.get(id=self.kwargs['pk'])
        if Read.objects.filter(read_user=user,notification_id=info).exists()==False:
            read = Read.objects.create(read_user=user,notification_id=info)
            read.save()
            
            #追記
            today = datetime.datetime.now()

            read2 = Read.objects.filter(read_user=user).count()
            if read2 > 0:
                info_all = Notification.objects.filter(Q(target_user_id = None)|Q(target_user_id = user),start_date__lte = today).distinct().count()
                no_read = info_all - read2
                if no_read > 99 :
                    context["no_read"] = "99+"
                else:
                    context["no_read"] = no_read
        
        context["user"] = user
        context["info"] = info
        return context

"""
ホーム画面
"""
class FileuploadListView(LoginRequiredMixin, ListView, CommonView):
    model = UploadManage
    template_name = 'draganddrop/fileup_home.html'
    form_class = ManageTasksStep1Form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """承認ワークフロー設定"""
        # ユーザーのApprovalWorkflowを取得
        approval_workflow = ApprovalWorkflow.objects.filter(reg_user_company=self.request.user.company.id).first()

        # 存在しなければ作成　※デフォルトの設定は承認ワークフローを"使用しない"
        if not approval_workflow:
            approval_workflow = ApprovalWorkflow.objects.create(
                reg_user = self.request.user.id,
                reg_user_company = self.request.user.company.id,
                registration_date = datetime.datetime.now()
            )
            approval_workflow.save()

        context["is_approval_workflow"] = approval_workflow.is_approval_workflow

        """一次承認者"""
        first_approver = FirstApproverRelation.objects.filter(company_id=self.request.user.company.id).first()
        context["first_approver"] = first_approver

        """二次承認者"""
        second_approver = SecondApproverRelation.objects.filter(company_id=self.request.user.company.id).first()

        """送信テーブル"""
        # 通常アップロード用
        user=self.request.user.id

        # 承認ワークフローを使用する場合
        if approval_workflow.is_approval_workflow == 1:

            # 一次承認者と二次承認者が設定されている場合
            if first_approver and second_approver:
                # 通常アップロード
                upload_manages = UploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0, application_status=5)# 最終承認済み
                # URL共有
                url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0, application_status=5)

            # 一次承認者しか設定されていない場合
            else:
                # 通常アップロード
                upload_manages = UploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0, application_status=3)# 一次承認済み
                # URL共有
                url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0, application_status=3)

        else:
            # 通常アップロード
            upload_manages = UploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0).exclude(application_status=6)# キャンセル
            # URL共有
            url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0).exclude(application_status=6)



        context["upload_manages"] = upload_manages
        print('ある？？？？？？？アップロード',upload_manages)
        # URLアップロード用
        # url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["url_upload_manages"] = url_upload_manages

        # OTPアップロード用
        otp_upload_manages = OTPUploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0)
        context["otp_upload_manages"] = otp_upload_manages

        """受信テーブル"""
        # ダウンロード用
        if approval_workflow.is_approval_workflow == 1:
            if first_approver and second_approver:
                upload_manage_for_dest_users = Downloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0, upload_manage__application_status=5)
            else:
                upload_manage_for_dest_users = Downloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0, upload_manage__application_status=3)
        else:
            upload_manage_for_dest_users = Downloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0)
        context["upload_manage_for_dest_users"] = upload_manage_for_dest_users

        # URLダウンロード用
        url_upload_manage_for_dest_users = UrlDownloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0)
        context["url_upload_manage_for_dest_users"] = url_upload_manage_for_dest_users
        # OTPダウンロード用
        otp_upload_manage_for_dest_users = OTPDownloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=0)
        context["otp_upload_manage_for_dest_users"] = otp_upload_manage_for_dest_users
        
        # ゲストアップロードダウンロード用
        guest_upload_manage_for_dest_users = GuestUploadDownloadtable.objects.filter(dest_user=self.request.user.email, trash_flag=0)
        context["guest_upload_manage_for_dest_users"] = guest_upload_manage_for_dest_users
        print('ゲストアップロードダウンロード',guest_upload_manage_for_dest_users)

        """ゴミ箱表示"""
        # アップロード用
        upload_manage_for_dest_users_deleted = Downloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=1)
        context["upload_manage_for_dest_users_deleted"] = upload_manage_for_dest_users_deleted

        # URLアップロード用
        url_upload_manage_for_dest_users_deleted = UrlDownloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=1)
        context["url_upload_manage_for_dest_users_deleted"] = url_upload_manage_for_dest_users_deleted
        
        # OTPアップロード用
        otp_upload_manage_for_dest_users_deleted = OTPDownloadtable.objects.filter(dest_user__email=self.request.user.email, trash_flag=1)
        context["otp_upload_manage_for_dest_users_deleted"] = otp_upload_manage_for_dest_users_deleted

        """会社毎のレコード数取得"""
        number_of_company_upload_manage = UploadManage.objects.filter(company=self.request.user.company.id, tmp_flag=0).all().count()
        context["number_of_company_upload_manage"] = number_of_company_upload_manage

        # セッションに「_(アンダースコア)以外のセッション情報があった場合削除
        for key in list(self.request.session.keys()):
            if not key.startswith("_"):
                del self.request.session[key]

        return context
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                    ユーザー管理関連
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""
イメージ削除(Ajax用)
"""
def delete_image(request):
    # print('削除Ajaxにきた')
    gen_image = request.POST.get('gen_image')
    # print('げんいめーーーーーーじ',gen_image)
    file = File.objects.filter(file=gen_image).first()
    # print('ファイル来てる？？？？？？？？',file)
    user = User.objects.filter(image=file.id).first()
    user.image = None
    user.save()
    is_deleted = file.delete()

    data = {
        'is_exist': is_deleted
    }
    if data['is_exist']:
        data['error_message'] = '現在設定している画像を削除しました'

    return JsonResponse(data)

"""
ユーザー情報変更画面
プロフィール情報編集アイコンから情報を変更する画面
"""
class UserUpdateInfoView(LoginRequiredMixin, UpdateView, CommonView):
    model = User
    template_name = "draganddrop/update_userinfomation.html"
    form_class = UserChangeForm
    login_url = '/login/'
# フォームに対してログインユーザーを渡す
    def get_form_kwargs(self):
        kwargs = super(UserUpdateInfoView, self).get_form_kwargs()
        return kwargs

    # ログインユーザーを返す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = User.objects.filter(pk=self.request.user.id).first()

        print('karenntoゆーざーきてるよーーー',current_user)
        #排他処理のタイムスタンプを上書きする
        # target_user.last_updated = datetime.now(timezone.utc)
        # target_user.is_updating = True
        # target_user.save()

        today = datetime.datetime.now()
        
        context = super().get_context_data(**kwargs)
        #すでにそのユーザーのレコードが存在してたたら（すでに利用中）

        if current_user.image:
            gen_image = File.objects.filter(pk=current_user.image.id)
            context["gen_image"] = current_user.image
        return context

    def form_valid(self, form):
        old_data = User.objects.filter(pk=self.request.user.id).first()
        user = form.save(commit=False)  

        # 姓と名をディスプレイ名にセットする
        last_name = form.cleaned_data['last_name']
        first_name = form.cleaned_data['first_name']
        middle_name = form.cleaned_data['middle_name']
        if last_name and first_name and middle_name:
            display_name = last_name + ' ' + middle_name + ' ' + first_name
            user.display_name = display_name
        elif last_name and first_name:
            display_name = last_name + ' ' + first_name
            user.display_name = display_name

        # ふりがなの姓と名をディスプレイ名にセットする
        p_last_name = form.cleaned_data['p_last_name']
        p_first_name = form.cleaned_data['p_first_name']
        p_middle_name = form.cleaned_data['p_middle_name']
        if p_last_name and p_first_name and p_middle_name:
            p_display_name = p_last_name + ' ' + p_middle_name + ' ' + p_first_name
            user.p_display_name = p_display_name
        elif p_last_name and p_first_name:
            p_display_name = p_last_name + ' ' + p_first_name
            user.p_display_name = p_display_name

        # 本番登録後、is_staff属性をTrueにする。
        user.is_staff = True

        # Serviceを登録する(UpdateViewで自動的にやってくれない？)
        # servicesはquerysetになっていて、object.set()で保存できる
        #services = form.cleaned_data['service']
        #user.service.set(services)
        old_image = ''

        print( 'せるふりくえすとせっしょん',self.request.session)
        print( 'おーるどでーた',old_data)
        if old_data.image:
            old_image = File.objects.filter(pk=old_data.image.id)
            print('オールドあります',old_image)
        
        if 'up_file_id' in self.request.session:
            print( 'ゆーざーいめーじ２２２２２２２',type(self.request.session['up_file_id']))
            user.image = File.objects.filter(id=self.request.session['up_file_id']).first()
            if old_image:
                print('おーるどいめーじあるよ！！！！！！！！！！',old_image)
                # old_image.delete()
        user.save()
        
        return redirect('draganddrop:home')
    

"""
プロファイル画像変更
"""
import json
class ImageImportView(View):
    def post(self, request, *args, **kwargs):
        upload_file = self.request.FILES.get('file')

        file, created = File.objects.get_or_create(name=upload_file.name,size=upload_file.size,file=upload_file,)

        file.save()
        up_file_id = file.id
        print('----------------------------------------------------------ふぁいるID',up_file_id)

        # 保存したファイルをセッションへ保存
        up_file_id_json = json.dumps(up_file_id)
        self.request.session['up_file_id'] = up_file_id_json
        print('イメージのセッション作成！！')
        # 何も返したくない場合、HttpResponseで返す
        return HttpResponse('OK')

###########################
# 関数 個人管理画面計算処理  #
###########################
def total_data_usage(object, company, user, download_table, download_file_table, file_size, type):
    # 通常アップロード
    if type == 1:
        personal_resource_manage, created = PersonalResourceManagement.objects.get_or_create(user = user)
        if created:
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_upload_manage = 1
            personal_resource_manage.number_of_download_table =  download_table
            personal_resource_manage.number_of_download_file_table = download_file_table
            personal_resource_manage.upload_manage_file_size = file_size
            personal_resource_manage.save()
        else:
            date = datetime.datetime.now()
            
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_upload_manage = UploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_download_table = download_table
            personal_resource_manage.number_of_download_file_table = download_file_table
            personal_resource_manage.upload_manage_file_size = file_size
            personal_resource_manage.save()
    
    # URL共有
    elif type == 2:
        personal_resource_manage, created = PersonalResourceManagement.objects.get_or_create(user = user)
        if created:
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_url_upload_manage = 1
            personal_resource_manage.number_of_url_download_table =  download_table
            personal_resource_manage.number_of_url_download_file_table = download_file_table
            personal_resource_manage.url_upload_manage_file_size = file_size
            personal_resource_manage.save()
        else:
            date = datetime.datetime.now()
            
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_url_download_table = download_table
            personal_resource_manage.number_of_url_download_file_table = download_file_table
            personal_resource_manage.url_upload_manage_file_size = file_size
            personal_resource_manage.save()
    
    # OTP共有
    elif type == 3:
        personal_resource_manage, created = PersonalResourceManagement.objects.get_or_create(user = user)
        if created:
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_otp_upload_manage = 1
            personal_resource_manage.number_of_otp_download_table =  download_table
            personal_resource_manage.number_of_otp_download_file_table = download_file_table
            personal_resource_manage.otp_upload_manage_file_size = file_size
            personal_resource_manage.save()
        else:
            date = datetime.datetime.now()

            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_otp_upload_manage = OTPUploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_otp_upload_manage = OTPUploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_otp_download_table = download_table
            personal_resource_manage.number_of_otp_download_file_table = download_file_table
            personal_resource_manage.otp_upload_manage_file_size = file_size
            personal_resource_manage.save()

    # ゲストアップロード共有
    else:
        personal_resource_manage, created = PersonalResourceManagement.objects.get_or_create(user = user)
        if created:
            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_guest_upload_manage = 1
            personal_resource_manage.number_of_guest_upload_download_table =  download_table
            personal_resource_manage.number_of_guest_upload_download_file_table = download_file_table
            personal_resource_manage.guest_upload_manage_file_size = file_size
            personal_resource_manage.save()
        else:
            date = datetime.datetime.now()

            personal_resource_manage.company = company
            personal_resource_manage.number_of_active_guest_upload_manage = GuestUploadManage.objects.filter(created_user=user, file_del_flag=0).all().count()
            personal_resource_manage.number_of_deactive_guest_upload_manage = GuestUploadManage.objects.filter(Q(created_user=user, file_del_flag=1, url_invalid_flag=False) | Q(created_user=user, end_date__lt=date, url_invalid_flag=False)).all().count() 
            personal_resource_manage.number_of_guest_upload_download_table = download_table
            personal_resource_manage.number_of_guest_upload_download_file_table = download_file_table
            personal_resource_manage.guest_upload_manage_file_size = file_size
            personal_resource_manage.save()


    # ファイルサイズ合計
    personal_resource_manage.total_file_size = personal_resource_manage.upload_manage_file_size + personal_resource_manage.url_upload_manage_file_size + personal_resource_manage.otp_upload_manage_file_size
    personal_resource_manage.save()

    # レコード総件数
    personal_resource_manage.total_record_size = (personal_resource_manage.number_of_active_upload_manage 
    + personal_resource_manage.number_of_deactive_upload_manage 
    + personal_resource_manage.number_of_active_url_upload_manage 
    + personal_resource_manage.number_of_deactive_url_upload_manage 
    + personal_resource_manage.number_of_active_otp_upload_manage 
    + personal_resource_manage.number_of_deactive_otp_upload_manage 
    + personal_resource_manage.number_of_download_table 
    + personal_resource_manage.number_of_download_file_table
    + personal_resource_manage.number_of_url_download_table
    + personal_resource_manage.number_of_url_download_file_table
    + personal_resource_manage.number_of_otp_download_table
    + personal_resource_manage.number_of_otp_download_file_table) * settings.DEFAULT_RECORD_SIZE

    # データ使用量
    personal_resource_manage.total_data_usage = personal_resource_manage.total_record_size + personal_resource_manage.total_file_size

    personal_resource_manage.save()

    return personal_resource_manage

###############################
# 関数 個人管理画面送信テーブル削除処理  #
###############################
def send_table_delete(user, download_table, download_file_table, file_size, type):
    date = datetime.datetime.now()
    personal_resource_manages = PersonalResourceManagement.objects.filter(user = user)
    for personal_resource_manage in personal_resource_manages:
        if type == 0:
            personal_resource_manage.number_of_active_upload_manage = UploadManage.objects.filter(created_user=user, file_del_flag=0, tmp_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(created_user=user, file_del_flag=1, tmp_flag=0) | Q(created_user=user, end_date__lt=date, tmp_flag=0)).all().count()
            personal_resource_manage.number_of_removed_upload_manage += 1
            personal_resource_manage.number_of_download_table -= download_table
            personal_resource_manage.number_of_download_file_table -= download_file_table
            personal_resource_manage.upload_manage_file_size -= file_size
            personal_resource_manage.save()
        elif type == 1:
            personal_resource_manage.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_removed_url_upload_manage += 1
            personal_resource_manage.number_of_url_download_table -= download_table
            personal_resource_manage.number_of_url_download_file_table -= download_file_table
            personal_resource_manage.url_upload_manage_file_size -= file_size
            personal_resource_manage.save()
        elif type == 2:
            personal_resource_manage.number_of_active_otp_upload_manage = OTPUploadManage.objects.filter(created_user=user, file_del_flag=0, end_date__gt=date).all().count()
            personal_resource_manage.number_of_deactive_otp_upload_manage = OTPUploadManage.objects.filter(Q(created_user=user, file_del_flag=1) | Q(created_user=user, end_date__lt=date)).all().count() 
            personal_resource_manage.number_of_removed_otp_upload_manage += 1
            personal_resource_manage.number_of_otp_download_table -= download_table
            personal_resource_manage.number_of_otp_download_file_table -= download_file_table
            personal_resource_manage.otp_upload_manage_file_size -= file_size
            personal_resource_manage.save()
        else:
            personal_resource_manage.number_of_active_guest_upload_manage = GuestUploadManage.objects.filter(created_user=user, file_del_flag=0).all().count()
            personal_resource_manage.number_of_deactive_guest_upload_manage = GuestUploadManage.objects.filter(created_user=user, end_date__lt=date, uploaded_date__isnull=True).all().count() 
            personal_resource_manage.number_of_removed_guest_upload_manage += 1
            personal_resource_manage.number_of_guest_upload_download_table -= download_table
            personal_resource_manage.number_of_guest_upload_download_file_table -= download_file_table
            personal_resource_manage.guest_upload_manage_file_size -= file_size
            personal_resource_manage.save()

    # ファイルサイズ合計
    personal_resource_manage.total_file_size = personal_resource_manage.upload_manage_file_size + personal_resource_manage.url_upload_manage_file_size + personal_resource_manage.otp_upload_manage_file_size + personal_resource_manage.guest_upload_manage_file_size
    personal_resource_manage.save()

    # レコード総件数
    print("-----", personal_resource_manage.number_of_url_download_file_table)
    personal_resource_manage.total_record_size = (personal_resource_manage.number_of_active_upload_manage 
    + personal_resource_manage.number_of_deactive_upload_manage 
    + personal_resource_manage.number_of_active_url_upload_manage 
    + personal_resource_manage.number_of_deactive_url_upload_manage
    + personal_resource_manage.number_of_active_otp_upload_manage 
    + personal_resource_manage.number_of_deactive_otp_upload_manage
    + personal_resource_manage.number_of_active_guest_upload_manage 
    + personal_resource_manage.number_of_deactive_guest_upload_manage
    + personal_resource_manage.number_of_download_table 
    + personal_resource_manage.number_of_download_file_table
    + personal_resource_manage.number_of_url_download_table
    + personal_resource_manage.number_of_url_download_file_table
    + personal_resource_manage.number_of_otp_download_table
    + personal_resource_manage.number_of_otp_download_file_table
    + personal_resource_manage.number_of_guest_upload_download_table
    + personal_resource_manage.number_of_guest_upload_download_file_table) * settings.DEFAULT_RECORD_SIZE
    # データ使用量
    personal_resource_manage.total_data_usage = personal_resource_manage.total_record_size + personal_resource_manage.total_file_size

    personal_resource_manage.save()

    return send_table_delete

###############################
# 関数 会社管理画面計算処理  #
###############################
def resource_management_calculation_process(company):
    # 個人管理データから同じ会社のオブジェクトを取得する
    personal_resource_manages = PersonalResourceManagement.objects.filter(company = company)

    # 会社管理データ作成・更新
    resource_manage, created = ResourceManagement.objects.get_or_create(company = company)
    download_table = 0
    url_download_table = 0
    otp_download_table = 0
    guest_download_table = 0
    download_file_table = 0
    url_download_file_table = 0
    otp_download_file_table = 0
    guest_download_file_table = 0
    total_file_size = 0
    number_of_active_upload_manage = 0
    number_of_deactive_upload_manage = 0
    number_of_active_url_upload_manage = 0
    number_of_deactive_url_upload_manage = 0
    number_of_active_otp_upload_manage = 0
    number_of_deactive_otp_upload_manage = 0
    number_of_active_guest_upload_manage = 0
    number_of_deactive_guest_upload_manage = 0
    number_of_removed_upload_manage = 0
    number_of_removed_url_upload_manage = 0
    number_of_removed_otp_upload_manage = 0
    number_of_removed_guest_upload_manage = 0
    for personal_resource_manage in personal_resource_manages:
        download_table += personal_resource_manage.number_of_download_table
        url_download_table += personal_resource_manage.number_of_url_download_table
        otp_download_table += personal_resource_manage.number_of_otp_download_table
        guest_download_table += personal_resource_manage.number_of_guest_upload_download_table
        download_file_table += personal_resource_manage.number_of_download_file_table
        url_download_file_table += personal_resource_manage.number_of_url_download_file_table
        otp_download_file_table += personal_resource_manage.number_of_otp_download_file_table
        guest_download_file_table += personal_resource_manage.number_of_guest_upload_download_file_table
        total_file_size += personal_resource_manage.total_file_size
        number_of_active_upload_manage += personal_resource_manage.number_of_active_upload_manage
        number_of_deactive_upload_manage += personal_resource_manage.number_of_deactive_upload_manage
        number_of_active_url_upload_manage += personal_resource_manage.number_of_active_url_upload_manage
        number_of_deactive_url_upload_manage += personal_resource_manage.number_of_deactive_url_upload_manage
        number_of_active_otp_upload_manage += personal_resource_manage.number_of_active_otp_upload_manage
        number_of_deactive_otp_upload_manage += personal_resource_manage.number_of_deactive_otp_upload_manage
        number_of_active_guest_upload_manage += personal_resource_manage.number_of_active_guest_upload_manage
        number_of_deactive_guest_upload_manage += personal_resource_manage.number_of_deactive_guest_upload_manage
        number_of_removed_upload_manage += personal_resource_manage.number_of_removed_upload_manage
        number_of_removed_url_upload_manage += personal_resource_manage.number_of_removed_url_upload_manage
        number_of_removed_otp_upload_manage += personal_resource_manage.number_of_removed_otp_upload_manage
        number_of_removed_guest_upload_manage += personal_resource_manage.number_of_removed_guest_upload_manage
        date = datetime.datetime.now()

        if created:
            resource_manage.number_of_active_upload_manage = number_of_active_upload_manage
            resource_manage.number_of_deactive_upload_manage = number_of_deactive_upload_manage
            resource_manage.number_of_active_url_upload_manage = number_of_active_url_upload_manage
            resource_manage.number_of_deactive_url_upload_manage = number_of_deactive_url_upload_manage
            resource_manage.number_of_active_otp_upload_manage = number_of_active_otp_upload_manage
            resource_manage.number_of_deactive_otp_upload_manage = number_of_deactive_otp_upload_manage
            resource_manage.number_of_active_guest_upload_manage = number_of_active_guest_upload_manage
            resource_manage.number_of_deactive_guest_upload_manage = number_of_deactive_guest_upload_manage

        else:
            resource_manage.number_of_active_upload_manage = UploadManage.objects.filter(company = company, file_del_flag=0, end_date__gt=date).all().count()
            resource_manage.number_of_deactive_upload_manage = UploadManage.objects.filter(Q(company=company, file_del_flag=1) | Q(company = company, end_date__lt=date)).all().count() 
            resource_manage.number_of_active_url_upload_manage = UrlUploadManage.objects.filter(company = company, file_del_flag=0, end_date__gt=date).all().count()
            resource_manage.number_of_deactive_url_upload_manage = UrlUploadManage.objects.filter(Q(company=company, file_del_flag=1) | Q(company = company, end_date__lt=date)).all().count() 
            resource_manage.number_of_active_otp_upload_manage = OTPUploadManage.objects.filter(company = company, file_del_flag=0, end_date__gt=date).all().count()
            resource_manage.number_of_deactive_otp_upload_manage = OTPUploadManage.objects.filter(Q(company=company, file_del_flag=1) | Q(company = company, end_date__lt=date)).all().count()
            resource_manage.number_of_active_guest_upload_manage = GuestUploadManage.objects.filter(company = company, file_del_flag=0).all().count()
            resource_manage.number_of_deactive_guest_upload_manage = GuestUploadManage.objects.filter(Q(company=company, file_del_flag=1) | Q(company = company, end_date__lt=date, url_invalid_flag=False)).all().count()  
            resource_manage.number_of_removed_upload_manage = number_of_removed_upload_manage
            resource_manage.number_of_removed_url_upload_manage = number_of_removed_url_upload_manage
            resource_manage.number_of_removed_otp_upload_manage = number_of_removed_otp_upload_manage 
            resource_manage.number_of_removed_guest_upload_manage = number_of_removed_guest_upload_manage 

        resource_manage.number_of_download_table = download_table
        resource_manage.number_of_download_file_table = download_file_table
        resource_manage.number_of_url_download_table = url_download_table
        resource_manage.number_of_url_download_file_table = url_download_file_table
        resource_manage.number_of_otp_download_table = otp_download_table
        resource_manage.number_of_otp_download_file_table = otp_download_file_table
        resource_manage.number_of_guest_upload_download_table = guest_download_table
        resource_manage.number_of_guest_upload_download_file_table = guest_download_file_table
        resource_manage.total_file_size = total_file_size
        resource_manage.save()

    # レコード総件数
    resource_manage.total_record_size = (resource_manage.number_of_active_upload_manage 
    + resource_manage.number_of_deactive_upload_manage 
    + resource_manage.number_of_active_url_upload_manage 
    + resource_manage.number_of_deactive_url_upload_manage
    + resource_manage.number_of_active_otp_upload_manage 
    + resource_manage.number_of_deactive_otp_upload_manage 
    + resource_manage.number_of_active_guest_upload_manage 
    + resource_manage.number_of_deactive_guest_upload_manage 
    + resource_manage.number_of_download_table 
    + resource_manage.number_of_download_file_table
    + resource_manage.number_of_url_download_table
    + resource_manage.number_of_url_download_file_table
    + resource_manage.number_of_otp_download_table
    + resource_manage.number_of_otp_download_file_table
    + resource_manage.number_of_guest_upload_download_table
    + resource_manage.number_of_guest_upload_download_file_table) * settings.DEFAULT_RECORD_SIZE

    # データ使用量
    resource_manage.total_data_usage = resource_manage.total_record_size + resource_manage.total_file_size

    resource_manage.save()

    return resource_management_calculation_process