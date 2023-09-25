from django.shortcuts import render
from django.views.generic import ListView, FormView, TemplateView
from draganddrop.views.home.home_common import CommonView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import UrlUploadManage, UrlDownloadtable
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
# フロントへメッセージ送信
from django.contrib import messages
# 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired

###########################
# URLアクセス画面#
###########################

class ApproveView(TemplateView):
    model = UrlUploadManage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URLを返す
        url_name = self.request.resolver_match.url_name
        context["url_name"] = url_name


    def get(self, request, token):
        # if request.method == "GET":
            # GET = ランダムURLにアクセスしてきた際

        timestamp_signer = TimestampSigner()

        if token:
                try:
                    # TOKENが有効なら
                    unsigned_token = timestamp_signer.unsign(token)


                    url_upload_manage = UrlUploadManage.objects.get(decode_token=unsigned_token)
                    end_date = url_upload_manage.end_date
                    auth_meth = url_upload_manage.auth_meth
                    

                    current_time = datetime.datetime.now(datetime.timezone.utc)
                    file_del_flag = url_upload_manage.file_del_flag

                    if end_date > current_time and file_del_flag==0:
                        if auth_meth == 1:
                            return HttpResponseRedirect(reverse('draganddrop:url_file_download_auth_mail', kwargs={'pk': url_upload_manage.id}))
                        else:
                            return HttpResponseRedirect(reverse('draganddrop:url_file_download_auth_pass', kwargs={'pk': url_upload_manage.id}))
                    elif end_date > current_time and file_del_flag == 1:
                        return HttpResponseRedirect(reverse('draganddrop:url_file_unable_download'))
                    else:
                        return HttpResponseRedirect(reverse('draganddrop:url_file_unable_download'))


                except SignatureExpired:
                    return render(request, self.template_name, context)

##################################
# URL共有 認証画面 メールアドレス ver #
##################################

class UrlFileDownloadAuthMail(FormView, CommonView):
    model = UrlUploadManage
    template_name = 'draganddrop/url_file_dl/url_file_dl_auth.html'
    form_class = UrlFileDownloadAuthMailForm

    def form_valid(self, form):
        email = self.request.POST.get('email') #formに入力したアドレスを取得
        self.request.session['email'] = email #次のDL画面でデータを取得するためsessionに保存
        
        url_upload_manage_id = self.kwargs['pk']
        url_upload_manage = UrlUploadManage.objects.filter(
            pk=url_upload_manage_id).first()

        if url_upload_manage.dest_user_group:
            group_email_list = []
            group_lists = url_upload_manage.dest_user_group.all()
            for group in group_lists:
                address_instances = group.address.all()
                for address_instance in address_instances:
                    group_email_list.append(address_instance.email)

        result_email = url_upload_manage.dest_user.filter(email=email).exists()
        
        if result_email or (email in group_email_list):
            return HttpResponseRedirect(reverse('draganddrop:url_file_download', kwargs={'pk': url_upload_manage.id}))
        else:
            messages.info(self.request, "正しいメールアドレスを入力して下さい")
            return HttpResponseRedirect(reverse('draganddrop:url_file_download_auth_mail', kwargs={'pk': url_upload_manage.id}))
            
##############################################
# URL共有 認証画面 メールアドレスとpassword ver #
##############################################

class UrlFileDownloadAuthPass(FormView, CommonView):

    model = UrlUploadManage
    template_name = 'draganddrop/url_file_dl/url_file_dl_auth.html'
    form_class = UrlFileDownloadAuthPassForm

    def form_valid(self, form):
        email = self.request.POST.get('email')  # formに入力したアドレスを取得
        self.request.session['email'] = email #次のDL画面でデータを取得するためsessionに保存

        password = self.request.POST.get('password')  # formに入力したパスワードを取得

        url_upload_manage_id = self.kwargs['pk']
        url_upload_manage = UrlUploadManage.objects.filter(
            pk=url_upload_manage_id).first()

        if url_upload_manage.dest_user_group:
            group_email_list = []
            group_lists = url_upload_manage.dest_user_group.all()
            for group in group_lists:
                address_instances = group.address.all()
                for address_instance in address_instances:
                    group_email_list.append(address_instance.email)

        result_email = url_upload_manage.dest_user.filter(email=email).exists()
        
        if result_email and url_upload_manage.password == password:
            return HttpResponseRedirect(reverse('draganddrop:url_file_download', kwargs={'pk': url_upload_manage.id}))
        elif email in group_email_list and url_upload_manage.password == password:
            return HttpResponseRedirect(reverse('draganddrop:url_file_download', kwargs={'pk': url_upload_manage.id}))
        else:
            messages.info(self.request, f'正しいメールアドレスまたはパスワードを入力して下さい。')
            return HttpResponseRedirect(reverse('draganddrop:url_file_download_auth_pass', kwargs={'pk': url_upload_manage.id}))

###########################
# URLファイルダウンロード画面  #
###########################

class UrlFileDownload(LoginRequiredMixin, ListView, CommonView):
    model = UrlUploadManage
    template_name = 'draganddrop/url_file_dl/url_file_dl.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        email = self.request.session['email'] #前画面で保存したsessionデータを取得(formに入力したアドレス)
       #個別ファイル用
        url_upload_manage_id = self.kwargs['pk']
        url_upload_manage = UrlUploadManage.objects.filter(
            pk=url_upload_manage_id, file_del_flag=0).first()
        context["url_upload_manage"] = url_upload_manage

        #Zipファイル用
        url_upload_manage_for_dest_users = UrlDownloadtable.objects.filter(
            url_upload_manage=url_upload_manage_id, dest_user__email=email, del_flag=False)
        context["url_upload_manage_for_dest_users"] = url_upload_manage_for_dest_users

        deleted_url_upload_manage = UrlDownloadtable.objects.filter(
            url_upload_manage=url_upload_manage_id, dest_user__email=email, del_flag=True)
        context["deleted_url_upload_manage"] = deleted_url_upload_manage

        return context

##################################
# URLファイルダウンロード 有効期限切れ  #
##################################

class UrlFileUnableDownload(ListView):
    model = UrlUploadManage
    template_name = 'draganddrop/url_file_dl/url_file_dl_auth.html'

    def index(request):
        return render(request, 'draganddrop/url_file_dl_auth.html')
