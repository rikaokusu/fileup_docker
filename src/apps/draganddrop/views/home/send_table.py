from django.shortcuts import render
from django.views.generic import View
from draganddrop.views.home.home_common import resource_management_calculation_process, send_table_delete
from draganddrop.models import Filemodel, UploadManage, Downloadtable, DownloadFiletable, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, OTPUploadManage, OTPDownloadtable, OTPDownloadFiletable
from django.http import JsonResponse
import urllib.parse
import os
from django.db.models import Q
from django.conf import settings
import zipfile

############################################
# 送信テーブル単数削除 #
############################################

class DeleteAjaxView(View):
    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        # is_type = request.POST.get('is_type')
        send_delete_id = request.POST.getlist('send_delete_id[]')
        send_delete_name = request.POST.get('send_delete_name')
        upload_manages = UploadManage.objects.filter(pk__in=send_delete_id)

        try:
            for upload_manage in upload_manages:

                #download_tableのレコード数を取得
                number_of_download_table = Downloadtable.objects.filter(upload_manage=upload_manage).all().count()

                # download_file_tableのレコード数を取得
                number_of_download_file_table = 0
                for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
                        number_of_download_file_table += int(downloadtable.downloadtable.all().count())

                files = upload_manage.file.all()
                upload_manage_file_size = 0
                for file in files:
                    # 管理テーブルから合計サイズをマイナスするためサイズデータ抽出する
                    upload_manage_file_size = upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:
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

                upload_manage.delete()

            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, number_of_download_table, number_of_download_file_table, upload_manage_file_size, 1)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

############################################
# 送信テーブル ファイルのみ削除 #
############################################

class FileDeleteAjaxView(View):
    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        # is_type = request.POST.get('is_type')
        send_delete_id = request.POST.getlist('send_delete_id[]')
        send_delete_name = request.POST.get('send_delete_name')
        upload_manages = UploadManage.objects.filter(pk__in=send_delete_id)

        try:
            for upload_manage in upload_manages:

                # del_flagを1に変更
                for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
                    downloadtable.del_flag = 1
                    downloadtable.save()
                    downloadfiletables = []
                    for downloadfiletable in DownloadFiletable.objects.filter(download_table=downloadtable).all():
                        downloadfiletable.del_flag = 1
                        downloadfiletables.append(downloadfiletable)
                    DownloadFiletable.objects.bulk_update(downloadfiletables, fields=['del_flag'])

                files = upload_manage.file.filter(del_flag=0).all()
                upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    upload_manage_file_size = upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:
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

                    # DBのfile_del_flagを1に変更しサイズを0にする
                    file.del_flag = 1
                    file.size = 0
                    file.save()

                    upload_manage.file_del_flag = 1
                    upload_manage.save()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, 0, 0, upload_manage_file_size, 1)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

##################################
# 送信テーブル URL共有の削除 #
##################################

class UrlDeleteAjaxView(View):
    def post(self, request):

        url_send_delete_id = request.POST.getlist('url_send_delete_id[]')
        url_send_delete_name = request.POST.get('url_send_delete_name')

        url_upload_manages = UrlUploadManage.objects.filter(pk__in=url_send_delete_id)

        try:
            for url_upload_manage in url_upload_manages:

                #download_tableのレコード数を取得
                number_of_url_download_table = UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all().count()

                # download_file_tableのレコード数を取得
                number_of_url_download_file_table = 0
                for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
                    number_of_url_download_file_table += int(urldownloadtable.url_download_table.all().count())

                # ファイルの実態が削除されていないデータのみ抽出する
                files = url_upload_manage.file.all()
                url_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするためサイズデータ抽出する
                    url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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

                url_upload_manage.delete()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, number_of_url_download_table, number_of_url_download_file_table, url_upload_manage_file_size, 2)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = url_send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

#######################################
# 送信テーブル URL共有 ファイルのみ削除 #
#######################################

class UrlFileDeleteAjaxView(View):
    def post(self, request):

        url_send_delete_id = request.POST.getlist('url_send_delete_id[]')
        url_send_delete_name = request.POST.get('url_send_delete_name')
        url_upload_manages = UrlUploadManage.objects.filter(pk__in=url_send_delete_id)

        try:
            for url_upload_manage in url_upload_manages:

                # del_flagを1に変更
                for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
                    urldownloadtable.del_flag= 1
                    urldownloadtable.save()
                    urldownloadfiletables = []
                    for urldownloadfiletable in UrlDownloadFiletable.objects.filter(url_download_table=urldownloadtable, del_flag=0).all():
                        urldownloadfiletable.del_flag = 1
                        urldownloadfiletables.append(urldownloadfiletable)
                    UrlDownloadFiletable.objects.bulk_update(urldownloadfiletables, fields=['del_flag'])

                files = url_upload_manage.file.filter(del_flag=0).all()
                url_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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

                    # DBのfile_del_flagを1に変更しサイズを0にする
                    file.del_flag = 1
                    file.size = 0
                    file.save()

                    url_upload_manage.file_del_flag = 1
                    url_upload_manage.save()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, 0, 0, url_upload_manage_file_size, 2)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = url_send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

##################################
# 送信テーブル OTPの削除 #
##################################

class OTPDeleteAjaxView(View):
    def post(self, request):

        otp_send_delete_id = request.POST.getlist('otp_send_delete_id[]')
        otp_send_delete_name = request.POST.get('otp_send_delete_name')
        otp_upload_manages = OTPUploadManage.objects.filter(pk__in=otp_send_delete_id)

        try:
            for otp_upload_manage in otp_upload_manages:

                #download_tableのレコード数を取得
                number_of_otp_download_table = OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all().count()

                # download_file_tableのレコード数を取得
                number_of_otp_download_file_table = 0
                for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
                    number_of_otp_download_file_table += int(otpdownloadtable.otp_download_table.all().count())

                # ファイルの実態が削除されていないデータのみ抽出する
                files = otp_upload_manage.file.all()
                otp_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするためサイズデータ抽出する
                    otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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

                otp_upload_manage.delete()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, number_of_otp_download_table, number_of_otp_download_file_table, otp_upload_manage_file_size, 3)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = otp_send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

#######################################
# 送信テーブル OTP ファイルのみ削除 #
#######################################

class OTPFileDeleteAjaxView(View):
    def post(self, request):

        otp_send_delete_id = request.POST.getlist('otp_send_delete_id[]')
        otp_send_delete_name = request.POST.get('otp_send_delete_name')

        otp_upload_manages = OTPUploadManage.objects.filter(pk__in=otp_send_delete_id)

        try:
            for otp_upload_manage in otp_upload_manages:

                # del_flagを1に変更
                for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
                    otpdownloadtable.del_flag= 1
                    otpdownloadtable.save()
                    otpdownloadfiletables = []
                    for otpdownloadfiletable in OTPDownloadFiletable.objects.filter(otp_download_table=otpdownloadtable, del_flag=0).all():
                        otpdownloadfiletable.del_flag = 1
                        otpdownloadfiletables.append(otpdownloadfiletable)
                    OTPDownloadFiletable.objects.bulk_update(otpdownloadfiletables, fields=['del_flag'])

                files = otp_upload_manage.file.filter(del_flag=0).all()
                otp_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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

                    # DBのfile_del_flagを1に変更しサイズを0にする
                    file.del_flag = 1
                    file.size = 0
                    file.save()

                    otp_upload_manage.file_del_flag = 1
                    otp_upload_manage.save()

            # PersonalResourceManagementテーブル情報を修正
            # 個人管理テーブルの作成・更新
            send_table_delete(self.request.user.id, 0, 0, otp_upload_manage_file_size, 3)
            # 会社管理テーブルの作成・更新
            resource_management_calculation_process(self.request.user.company.id)

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = otp_send_delete_name + 'を削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

##################################
# 送信テーブル一括削除  #
##################################
class SendTableMultiDeleteAjaxView(View):
    def post(self, request):
        upload_manage_deleted_ids = request.POST.getlist('upload_manage_delete_ids[]')
        try:
            upload_manages = UploadManage.objects.filter(pk__in=upload_manage_deleted_ids)
            url_upload_manages = UrlUploadManage.objects.filter(pk__in=upload_manage_deleted_ids)
            otp_upload_manages = OTPUploadManage.objects.filter(pk__in=upload_manage_deleted_ids)

            for upload_manage in upload_manages:

                #download_tableのレコード数を取得
                number_of_download_table = Downloadtable.objects.filter(upload_manage=upload_manage).all().count()

                # download_file_tableのレコード数を取得
                number_of_download_file_table = 0
                for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
                        number_of_download_file_table += int(downloadtable.downloadtable.all().count())

                files = upload_manage.file.all()
                upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    upload_manage_file_size = upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:
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
                            os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))

                    # DBの対象行を削除
                    file.delete()

                upload_manage.delete()

                # PersonalResourceManagementテーブル情報を修正
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, number_of_download_table, number_of_download_file_table, upload_manage_file_size, 1)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)


            for url_upload_manage in url_upload_manages:

                #url_download_tableのレコード数を取得
                number_of_url_download_table = UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all().count()

                # download_url_file_tableのレコード数を取得
                number_of_url_download_file_table = 0
                for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
                        number_of_url_download_file_table += int(urldownloadtable.url_download_table.all().count())

                files = url_upload_manage.file.all()
                url_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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
                            os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))

                    # DBの対象行を削除
                    file.delete()

                url_upload_manage.delete()

                # PersonalResourceManagementテーブル情報を修正
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, number_of_url_download_table, number_of_url_download_file_table, url_upload_manage_file_size, 2)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)
            
            for otp_upload_manage in otp_upload_manages:

                #otp_download_tableのレコード数を取得
                number_of_otp_download_table = OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all().count()

                # download_otp_file_tableのレコード数を取得
                number_of_otp_download_file_table = 0
                for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
                        number_of_otp_download_file_table += int(otpdownloadtable.otp_download_table.all().count())

                files = otp_upload_manage.file.all()
                otp_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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
                            os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))

                    # DBの対象行を削除
                    file.delete()

                otp_upload_manage.delete()

                # PersonalResourceManagementテーブル情報を修正
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, number_of_otp_download_table, number_of_otp_download_file_table, otp_upload_manage_file_size, 3)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)


            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = '削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

##################################
# 送信テーブル ファイルのみ一括削除  #
##################################
class SendTableFileMultiDeleteAjaxView(View):
    def post(self, request):
        upload_manage_deleted_ids = request.POST.getlist('upload_manage_delete_ids[]')

        try:
            upload_manages = UploadManage.objects.filter(pk__in=upload_manage_deleted_ids)
            url_upload_manages = UrlUploadManage.objects.filter(pk__in=upload_manage_deleted_ids)
            otp_upload_manages = OTPUploadManage.objects.filter(pk__in=upload_manage_deleted_ids)

            for upload_manage in upload_manages:
                                
                # del_flagを1に変更
                for downloadtable in Downloadtable.objects.filter(upload_manage=upload_manage).all():
                    downloadtable.del_flag = 1
                    downloadtable.save()
                    downloadfiletables = []
                    for downloadfiletable in DownloadFiletable.objects.filter(download_table=downloadtable).all():
                        downloadfiletable.del_flag = 1
                        downloadfiletables.append(downloadfiletable)
                    DownloadFiletable.objects.bulk_update(downloadfiletables, fields=['del_flag'])

                files = upload_manage.file.all()
                upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    upload_manage_file_size = upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:
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
                            os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))

                    # DBのfile_del_flagを1に変更しサイズを0にする
                    file.del_flag = 1
                    file.size = 0
                    file.save()

                    upload_manage.file_del_flag = 1
                    upload_manage.save()

                # PersonalResourceManagementテーブル情報を修正
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, 0, 0, upload_manage_file_size, 1)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)


            for url_upload_manage in url_upload_manages:

                # del_flagを1に変更
                for urldownloadtable in UrlDownloadtable.objects.filter(url_upload_manage=url_upload_manage).all():
                    urldownloadtable.del_flag= 1
                    urldownloadtable.save()
                    urldownloadfiletables = []
                    for urldownloadfiletable in UrlDownloadFiletable.objects.filter(url_download_table=urldownloadtable).all():
                        urldownloadfiletable.del_flag = 1
                        urldownloadfiletables.append(urldownloadfiletable)
                    UrlDownloadFiletable.objects.bulk_update(urldownloadfiletables, fields=['del_flag'])

                files = url_upload_manage.file.all()
                url_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    url_upload_manage_file_size = url_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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
                            os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))

                    # DBのfile_del_flagを1に変更しサイズを0にする
                    file.del_flag = 1
                    file.size = 0
                    file.save()

                    url_upload_manage.file_del_flag = 1
                    url_upload_manage.save()

                # PersonalResourceManagementテーブル情報を修正
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, 0, 0, url_upload_manage_file_size, 2)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)

            for otp_upload_manage in otp_upload_manages:

                # del_flagを1に変更
                for otpdownloadtable in OTPDownloadtable.objects.filter(otp_upload_manage=otp_upload_manage).all():
                    otpdownloadtable.del_flag= 1
                    otpdownloadtable.save()
                    otpdownloadfiletables = []
                    for otpdownloadfiletable in OTPDownloadFiletable.objects.filter(otp_download_table=otpdownloadtable).all():
                        otpdownloadfiletable.del_flag = 1
                        otpdownloadfiletables.append(otpdownloadfiletable)
                    OTPDownloadFiletable.objects.bulk_update(otpdownloadfiletables, fields=['del_flag'])

                files = otp_upload_manage.file.all()
                otp_upload_manage_file_size = 0
                for file in files:

                    # 管理テーブルから合計サイズをマイナスするために削除するファイルのサイズを取得
                    otp_upload_manage_file_size = otp_upload_manage_file_size + int(file.size)

                    # 複製データがある場合はファイルの実体は削除しない
                    file_upload = file.upload
                    file_num = Filemodel.objects.filter(upload=file_upload).all().count()
                    if file_num == 1:

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
                            os.remove(os.path.join(settings.FULL_MEDIA_ROOT, file_name))

                    # DBのfile_del_flagを1に変更しサイズを0にする
                    file.del_flag = 1
                    file.size = 0
                    file.save()

                    otp_upload_manage.file_del_flag = 1
                    otp_upload_manage.save()

                # PersonalResourceManagementテーブル情報を修正
                # 個人管理テーブルの作成・更新
                send_table_delete(self.request.user.id, 0, 0, otp_upload_manage_file_size, 3)
                # 会社管理テーブルの作成・更新
                resource_management_calculation_process(self.request.user.company.id)


            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = '削除しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)