from django.shortcuts import render
from django.views.generic import View
from draganddrop.views.home.home_common import resource_management_calculation_process, send_table_delete
from draganddrop.models import Filemodel, UploadManage, Downloadtable, DownloadFiletable, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, OTPDownloadtable, OTPDownloadFiletable
from django.http import JsonResponse
import urllib.parse
import os
from django.db.models import Q
from django.conf import settings
import zipfile

##################################
# 受信テーブル単数削除  #
##################################
class DownloadTableDeleteAjaxView(View):
    def post(self, request):
        delete_id = request.POST.get('delete_id')
        delete_name = request.POST.get('delete_name')

        try:
            # ダウンロードテーブルに変更
            downloadtable = Downloadtable.objects.get(pk__exact=delete_id)
            # ダウンロードテーブルのゴミ箱フラグを1に変更する
            downloadtable.trash_flag = 1
            downloadtable.save()

            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:
            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = str(e)
            return JsonResponse(data)

##################################
# 受信テーブル URL共有 単数削除 #
##################################
class UrlDownloadTableDeleteAjaxView(View):
    def post(self, request):
        url_delete_id = request.POST.get('url_delete_id')
        url_delete_name = request.POST.get('url_delete_name')

        try:
            # ダウンロードテーブルに変更
            urldownloadtable = UrlDownloadtable.objects.get(pk__exact=url_delete_id)

            # ダウンロードテーブルの削除フラグを立てる
            urldownloadtable.trash_flag = 1

            # その後保存する
            urldownloadtable.save()

            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = url_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:
            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = str(e)
            return JsonResponse(data)
        
##################################
# 受信テーブル OTP 単数削除 #
##################################
class OTPDownloadTableDeleteAjaxView(View):
    def post(self, request):
        otp_delete_id = request.POST.get('otp_delete_id')
        otp_delete_name = request.POST.get('otp_delete_name')

        try:
            # ダウンロードテーブルに変更
            otpdownloadtable = OTPDownloadtable.objects.get(pk__exact=otp_delete_id)

            # ダウンロードテーブルの削除フラグを立てる
            otpdownloadtable.trash_flag = 1

            # その後保存する
            otpdownloadtable.save()

            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = otp_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:
            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = str(e)
            return JsonResponse(data)

##################################
# 受信テーブル一括削除 #
##################################
class MultiDownloadTableDeleteAjaxView(View):
    def post(self, request):
        multi_delete_id = request.POST.getlist('dest_user_ids[]')
        url_multi_delete_id = request.POST.getlist('url_dest_user_ids[]')
        otp_multi_delete_id = request.POST.getlist('otp_dest_user_ids[]')

        try:
            # ダウンロードテーブルに変更
            multi_tables = Downloadtable.objects.filter(pk__in=multi_delete_id)
            multi_tables = multi_tables.all()

            url_multi_tables = UrlDownloadtable.objects.filter(pk__in=url_multi_delete_id)
            url_multi_tables = url_multi_tables.all()
            
            otp_multi_tables = OTPDownloadtable.objects.filter(pk__in=otp_multi_delete_id)
            otp_multi_tables = otp_multi_tables.all()

            # ダウンロードテーブルに紐づいているファイルのQSを取得
            if multi_tables:
                for multi_table in multi_tables:
                    multi_table.trash_flag = 1

                    multi_table.save()

            elif url_multi_tables:
                for url_multi_table in url_multi_tables:
                    url_multi_table.trash_flag = 1

                    url_multi_table.save()
            
            else:
                for otp_multi_table in otp_multi_tables:
                    otp_multi_table.trash_flag = 1

                    otp_multi_table.save()

            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = '一括削除しました'
            return JsonResponse(data)

        except:
            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '一括削除に失敗しました'
            return JsonResponse(data)

##################################
# ゴミ箱からの復元  #
##################################

class RestoreAjaxView(View):
    def post(self, request):
        deleted_ids = request.POST.getlist('deleted_ids[]')

        try:
            download_tables = Downloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)
            download_tables = download_tables.all()

            url_download_tables = UrlDownloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)
            url_download_tables = url_download_tables.all()
            
            otp_download_tables = OTPDownloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)
            otp_download_tables = otp_download_tables.all()

            for download_table in download_tables:

                download_table.trash_flag = 0
                download_table.save()

            for url_download_table in url_download_tables:
                url_download_file_tables = UrlDownloadFiletable.objects.filter(url_download_table=url_download_table)
                files = url_download_file_tables.all()

                url_download_table.trash_flag = 0
                url_download_table.save()
            
            for otp_download_table in otp_download_tables:
                otp_download_file_tables = OTPDownloadFiletable.objects.filter(otp_download_table=otp_download_table)
                files = otp_download_file_tables.all()

                otp_download_table.trash_flag = 0
                otp_download_table.save()

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = delete_name + 'を復元しました'
            return JsonResponse(data)

        except:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '復元に失敗しました'
            return JsonResponse(data)


##################################
# ゴミ箱 単数削除  #
##################################
class TrashDeleteAjaxView(View):
    def post(self, request):
        delete_id = request.POST.get('delete_id')
        delete_name = request.POST.get('delete_name')

        try:
            downloadtable = Downloadtable.objects.get(pk__exact=delete_id)
            downloadtable.trash_flag = 2
            downloadtable.save()
            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:

            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)


##################################
# URL共有 ゴミ箱 単数削除  #
##################################
class UrlTrashDeleteAjaxView(View):
    def post(self, request):
        url_delete_id = request.POST.get('url_delete_id')
        url_delete_name = request.POST.get('url_delete_name')

        try:
            urldownloadtable = UrlDownloadtable.objects.get(pk__exact=url_delete_id)
            urldownloadtable.trash_flag = 2
            urldownloadtable.save()


            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = url_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:

            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

##################################
# OTP ゴミ箱 単数削除  #
##################################
class OTPTrashDeleteAjaxView(View):
    def post(self, request):
        otp_delete_id = request.POST.get('otp_elete_id')
        otp_delete_name = request.POST.get('otp_delete_name')

        try:
            otpdownloadtable = OTPDownloadtable.objects.get(pk__exact=otp_delete_id)
            otpdownloadtable.trash_flag = 2
            otpdownloadtable.save()


            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = otp_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:

            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = '削除に失敗しました'
            return JsonResponse(data)

##################################
# ゴミ箱 一括削除  #
##################################

class MultiDeleteAjaxView(View):
    def post(self, request):
        deleted_ids = request.POST.getlist('deleted_ids[]')

        try:
            download_tables = Downloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)
            url_download_tables = UrlDownloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)
            otp_download_tables = OTPDownloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)

            # Downloadfiletableの該当する行も削除する
            for download_table in download_tables:

                download_table.trash_flag = 2
                download_table.save()

            for url_download_table in url_download_tables:
                url_download_file_tables = UrlDownloadFiletable.objects.filter(url_download_table=url_download_table)

                url_download_table.trash_flag = 2
                url_download_table.save()
            
            for otp_download_table in otp_download_tables:
                otp_download_file_tables = OTPDownloadFiletable.objects.filter(otp_download_table=otp_download_table)

                otp_download_table.trash_flag = 2
                otp_download_table.save()

            # メッセージを格納してJSONで返す
            data = {}
            data['message'] = '削除しました'
            return JsonResponse(data)

        except Exception as e:
            # 失敗時のメッセージを格納してJASONで返す
            data = {}
            # data ['message'] = '削除に失敗しました'
            data['error'] = str(e)
            return JsonResponse(data)

