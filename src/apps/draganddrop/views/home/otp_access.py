from django.shortcuts import render
from django.views.generic import View, ListView, FormView, TemplateView
from draganddrop.views.home.home_common import CommonView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import OTPFileDownloadAuthForm
from draganddrop.models import OTPUploadManage, OTPDownloadtable
from django.urls import reverse
from django.http import HttpResponseRedirect

import datetime
# フロントへメッセージ送信
from django.contrib import messages
# 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired
import random
from dateutil.relativedelta import relativedelta
# テンプレート情報取得
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.core.mail import BadHeaderError,send_mail
from django.http import JsonResponse
import json
###########################
# OTPアクセス画面#
###########################

class OTPApproveView(TemplateView):
    model = OTPUploadManage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URLを返す
        url_name = self.request.resolver_match.url_name
        context["url_name"] = url_name
        return context

    def get(self, request, token):
        
        # if request.method == "GET":
            # GET = ランダムURLにアクセスしてきた際

        timestamp_signer = TimestampSigner()

        if token:
            try:
                # TOKENが有効なら
                unsigned_token = timestamp_signer.unsign(token)

                otp_upload_manage = OTPUploadManage.objects.get(decode_token=unsigned_token)
                end_date = otp_upload_manage.end_date
                current_time = datetime.datetime.now(datetime.timezone.utc)
                file_del_flag = otp_upload_manage.file_del_flag

                if end_date > current_time and file_del_flag==0:
                    otp_upload_manage_id = str(otp_upload_manage.id)
                    self.request.session['otp_upload_manage_id'] = otp_upload_manage_id
                    return HttpResponseRedirect(reverse('draganddrop:otp_file_download_auth', kwargs={'pk': otp_upload_manage.id}))
                elif end_date > current_time and file_del_flag == 1:
                    return HttpResponseRedirect(reverse('draganddrop:otp_file_unable_download'))
                else:
                    return HttpResponseRedirect(reverse('draganddrop:otp_file_unable_download'))


            except SignatureExpired:
                return render(request, self.template_name)
                # return render(request, self.template_name, context)

##################################
# OTP 認証画面 #
##################################
class OTPFileDownloadAuth(FormView):

    model = OTPUploadManage
    template_name = 'draganddrop/otp_file_dl/otp_file_dl_auth.html'
    form_class = OTPFileDownloadAuthForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_name = self.request.resolver_match.url_name

        context["url_name"] = url_name
        return context

    def form_valid(self, form):
        email = self.request.POST.get('email') #formに入力したアドレスを取得
        password = self.request.POST.get('password')  # formに入力したパスワードを取得
        self.request.session['email'] = email #次のDL画面でデータを取得するためsessionに保存
        otp_upload_manage_id = self.kwargs['pk']
        otp_upload_manage = OTPUploadManage.objects.filter(
            pk=otp_upload_manage_id).first()

        if otp_upload_manage.dest_user_group:
            group_email_list = []
            group_lists = otp_upload_manage.dest_user_group.all()
            for group in group_lists:
                address_instances = group.address.all()
                for address_instance in address_instances:
                    group_email_list.append(address_instance.email)

        result_email = otp_upload_manage.dest_user.filter(email=email).exists()
        now =  datetime.datetime.now(datetime.timezone.utc)
        five_min = otp_upload_manage.password_create_time + datetime.timedelta(minutes=5)
        if result_email and otp_upload_manage.password == password:
            if five_min > now:
                #OTP一致でファイル表示
                self.request.session['otp_result'] = 'success' #次のDL画面への不正遷移防止のためsessionに保存
                return HttpResponseRedirect(reverse('draganddrop:otp_file_download', kwargs={'pk': otp_upload_manage.id}))
            else:
                messages.info(self.request, "ワンタイムパスワードの有効期限が切れています。")
                return HttpResponseRedirect(reverse('draganddrop:otp_file_download_auth', kwargs={'pk': otp_upload_manage.id}))
        elif email in group_email_list and otp_upload_manage.password == password:
            if five_min > now:
                #OTP一致でファイル表示
                self.request.session['otp_result'] = 'success' #次のDL画面への不正遷移防止のためsessionに保存
                return HttpResponseRedirect(reverse('draganddrop:otp_file_download', kwargs={'pk': otp_upload_manage.id}))
            else:
                messages.info(self.request, "ワンタイムパスワードの有効期限が切れています。")
                return HttpResponseRedirect(reverse('draganddrop:otp_file_download_auth', kwargs={'pk': otp_upload_manage.id}))
        else:
            messages.info(self.request, "正しいメールアドレスまたはワンタイムパスワードを入力して下さい")
            return HttpResponseRedirect(reverse('draganddrop:otp_file_download_auth', kwargs={'pk': otp_upload_manage.id}))

##################################
# OTP パスワード送信Ajax #
##################################
class OTPSendAjaxView(View):
    
    def post(self, request):
        otp_upload_manage_id = self.request.session['otp_upload_manage_id']
        email = request.POST.get('email')
    
        otp_upload_manage = OTPUploadManage.objects.filter(
            pk=otp_upload_manage_id).first()

        if otp_upload_manage.dest_user_group:
            group_email_list = []
            group_lists = otp_upload_manage.dest_user_group.all()
            for group in group_lists:
                address_instances = group.address.all()
                for address_instance in address_instances:
                    group_email_list.append(address_instance.email)

        result_email = otp_upload_manage.dest_user.filter(email=email).exists()

        if result_email or (email in group_email_list):
            #OTPを送る処理
            #パスワード生成(６桁の数字　制限時間５分)
            random_number = random.randint(100000, 999999)
            pw = random_number
            otp_upload_manage.password = pw
            otp_upload_manage.password_create_time = datetime.datetime.now()

            otp_upload_manage.save()

            # OTPの送付
            context = {
                'pw':pw,
                'email': email,
            }

            subject_template = get_template('draganddrop/otp_file_dl/mail_template/subject.txt')
            subject = subject_template.render(context)

            message_template = get_template('draganddrop/otp_file_dl/mail_template/message.txt')
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

###########################
# OTPファイルダウンロード画面  #
###########################

class OTPFileDownload(ListView):
    model = OTPUploadManage
    template_name = 'draganddrop/otp_file_dl/otp_file_dl.html'

    def dispatch(self, request, *args, **kwargs):
        # 不正遷移check
        if not 'otp_result' in self.request.session:
                return HttpResponseRedirect(reverse('draganddrop:home'))

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        email = self.request.session['email'] #前画面で保存したsessionデータを取得(formに入力したアドレス)
        #個別ファイル用
        otp_upload_manage_id = self.kwargs['pk']
        otp_upload_manage = OTPUploadManage.objects.filter(
            pk=otp_upload_manage_id, file_del_flag=0).first()
        context["otp_upload_manage"] = otp_upload_manage

        #Zipファイル用
        otp_upload_manage_for_dest_users = OTPDownloadtable.objects.filter(
            otp_upload_manage=otp_upload_manage_id, dest_user__email=email, del_flag=False)
        context["otp_upload_manage_for_dest_users"] = otp_upload_manage_for_dest_users

        deleted_otp_upload_manage = OTPDownloadtable.objects.filter(
            otp_upload_manage=otp_upload_manage_id, dest_user__email=email, del_flag=True)
        context["deleted_otp_upload_manage"] = deleted_otp_upload_manage

        return context       

##################################
# OTPファイルダウンロード 有効期限切れ  #
##################################

class OTPFileUnableDownload(ListView):
    model = OTPUploadManage
    template_name = 'draganddrop/otp_file_dl/otp_file_dl.html'

    def index(request):
        return render(request, 'draganddrop/otp_file_dl/otp_file_dl.html')