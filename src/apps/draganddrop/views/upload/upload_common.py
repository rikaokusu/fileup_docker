from django.shortcuts import render
from django.views.generic import View
from ...forms import FileForm, ManageTasksStep1Form, DummyForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksUrlStep1Form, UrlDistFileUploadForm, UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
from draganddrop.views.home.home_common import resource_management_calculation_process, send_table_delete
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
import urllib.parse
import os
from django.conf import settings
from rest_framework import status
# 全てで実行させるView
from django.core.signing import TimestampSigner, dumps, SignatureExpired

################################################
# ファイルアップロード直後にFilemodelオブジェクト作成 #
################################################
class FileUpload(View):
    def post(self, request, *args, **kwargs):

        up_file_id = []
        up_file_name = []

        # １回目の処理を保存
        if 'up_file_name' in self.request.session:
            up_file_name.extend(self.request.session['up_file_name'])

        for upload_file in self.request.FILES.values():

            file, created = Filemodel.objects.get_or_create(
                name=upload_file.name,
                size=upload_file.size,
                upload=upload_file,
            )

            file.save()

            up_file_id.append(file.id)
            up_file_name.append(file.name)

        # 保存したファイルをセッションへ保存
        up_file_id_json = json.dumps(up_file_id)
        self.request.session['up_file_id'] = up_file_id_json
        self.request.session['up_file_name'] = up_file_name

        # 何も返したくない場合、HttpResponseで返す
        return HttpResponse("OK")

##################################
# DropZone アップロードファイルの削除  #
##################################
class DropZoneFileDeleteView(View):
    def post(self, request, *args, **kwargs):
        try:
            file_pk = request.POST.get('file_pk')
            url_name = request.POST.get('url_name')
            #対象ファイルをDBから取得
            filemodel_obj = Filemodel.objects.filter(pk=file_pk).first()
            delete_file_size = int(filemodel_obj.size)
            # 複製データがある場合はファイルの実体は削除しない
            file_upload = filemodel_obj.upload
            file_num = Filemodel.objects.filter(upload=file_upload).all().count()
            if file_num == 1:
                # 実ファイル名を文字列にデコード
                file_path = urllib.parse.unquote(filemodel_obj.upload.url)
                # ファイルパスを分割してファイル名だけ取得
                file_name = file_path.split('/', 3)[3]
                # パスを取得
                path = os.path.join(settings.FULL_MEDIA_ROOT, file_name)
                # パスの存在確認
                result = os.path.exists(path)
                if result:
                    # 絶対パスでファイル実体を削除
                    os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))
            
            if url_name == "step2_update" :
                # ログインユーザーが作成したupload_manageを取得
                personal_user_upload_manages = UploadManage.objects.filter(created_user=self.request.user.id, tmp_flag=0).all()
                for personal_user_upload_manage in personal_user_upload_manages:
                    # download_file_tableのレコード数を取得
                    download_file_table = DownloadFiletable.objects.filter(download_file=file_pk).all().count()
                
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, 0, download_file_table, delete_file_size, 1)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)

            elif url_name == "step2_url_update" :
                personal_user_url_upload_manages = UrlUploadManage.objects.filter(created_user=self.request.user.id).all()
                url_upload_manage_file_size = 0

                for personal_user_url_upload_manage in personal_user_url_upload_manages:
                    # url_download_file_tableのレコード数を取得
                    url_download_file_table = UrlDownloadFiletable.objects.filter(download_file=file_pk).all().count()

                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, 0, url_download_file_table, delete_file_size, 2)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)

            else:
                pass
            
            # 対象オブジェクトを削除
            filemodel_obj.delete()

            # メッセージを生成してJSONで返す
            return JsonResponse({"status": "ok",
                                "message": "アップロードファイルを削除しました",
                                 })
                        
        except Exception as e:
            data = {}
            data['status'] = 'ng'
            data['message'] = 'アップロードファイルの削除に失敗しました'
            return JsonResponse(data)

###########################
# キャンセル処理 #
###########################
class CancelView(View):
        
    def get(self, request, *args, **kwargs):

        # セッションに「managetasksstep1form_id」があれば、取得した行を削除
        if 'upload_manage_id' in request.session:
            upload_manage_tmp = UploadManage.objects.filter(pk=request.session['upload_manage_id']).first()
            files = upload_manage_tmp.file.all()
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
                    os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))
                # DBの対象行を削除
                file.delete()

            upload_manage_tmp.delete()

        # セッションに「managetasksstep1form_id」があれば、取得した行を削除
        if 'url_upload_manage_id' in request.session:
            url_upload_manage = UrlUploadManage.objects.filter(pk=request.session['url_upload_manage_id']).first()
            files = url_upload_manage.file.all()
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
                    os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))
                # DBの対象行を削除
                file.delete()

            url_upload_manage.delete()
        # セッションに「_(アンダースコア)以外のセッション情報があった場合削除
        for key in list(self.request.session.keys()):
            if not key.startswith("_"):
                del self.request.session[key]

        return HttpResponseRedirect(reverse('draganddrop:home'))