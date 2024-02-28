from django.shortcuts import render
from django.views.generic import View
from draganddrop.views.home.home_common import resource_management_calculation_process, send_table_delete
from draganddrop.models import Filemodel, UploadManage, Downloadtable, DownloadFiletable, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, OTPDownloadtable, OTPDownloadFiletable, OTPUploadManage, ApprovalManage, ApprovalLog, GuestUploadDownloadtable, GuestUploadDownloadFiletable, GuestUploadManage
from django.http import JsonResponse
from draganddrop.views.home.home_common import CommonView
import urllib.parse
import os
from django.db.models import Q
from django.conf import settings
import zipfile
#操作ログ関数
from lib.my_utils import add_log

# 時刻取得
from datetime import datetime, timedelta

##################################
# 受信テーブル単数削除  #
##################################
class DownloadTableDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):

        print('----------------- DownloadTableDeleteAjaxView')

        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        delete_id = request.POST.get('delete_id') #downloadtableのid
        delete_name = request.POST.get('delete_name')#ファイルタイトル

        try:
            # ダウンロードテーブルに変更
            downloadtable = Downloadtable.objects.get(pk__exact=delete_id)
            #操作ログ用・ファイル名取得
            uploadmanage = UploadManage.objects.get(id=downloadtable.upload_manage.id)
            # ファイル名
            upload_files = uploadmanage.file.all()
            files = []
            for file in upload_files:
                print('ふぁいるかくにん1',file.name)           
                file_name = file.name + "\r\n"
                files.append(file_name)
            files = ' '.join(files)
            # files = uploadmanage.file.all()
            #操作ログ終わり
            # ダウンロードテーブルのゴミ箱フラグを1に変更する
            downloadtable.trash_flag = 1
            downloadtable.save()
            # 操作ログ登録
            add_log(2,3,current_user,current_user.company,delete_name,files,"",0,self.request.META.get('REMOTE_ADDR'))

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
class UrlDownloadTableDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        url_delete_id = request.POST.get('url_delete_id')#downloadtableのid 
        url_delete_name = request.POST.get('url_delete_name')#ファイルタイトル

        try:
            # ダウンロードテーブルに変更
            urldownloadtable = UrlDownloadtable.objects.get(pk__exact=url_delete_id)
            #↓二行操作ログ用・ファイル名取得
            urluploadmanage = UrlUploadManage.objects.get(id=urldownloadtable.url_upload_manage.id)
            print('urlもしかしてfileみえない？1',urluploadmanage)
            # ファイル名
            url_upload_files = urluploadmanage.file.all()
            files = []
            for file in url_upload_files:       
                file_name = file.name + "\r\n"
                files.append(file_name)
            files = ' '.join(files)
            # files = urluploadmanage.file.all()
            # ダウンロードテーブルの削除フラグを立てる
            urldownloadtable.trash_flag = 1

            # その後保存する
            urldownloadtable.save()
            # 操作ログ登録
            print('urlもしかしてfileみえない？3',files)
            add_log(2,3,current_user,current_user.company,url_delete_name,files,"",1,self.request.META.get('REMOTE_ADDR'))
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
class OTPDownloadTableDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        otp_delete_id = request.POST.get('otp_delete_id')
        otp_delete_name = request.POST.get('otp_delete_name')

        try:
            # ダウンロードテーブルに変更
            otpdownloadtable = OTPDownloadtable.objects.get(pk__exact=otp_delete_id)
            #↓二行操作ログ用・ファイル名取得
            otpuploadmanage = OTPUploadManage.objects.get(id=otpdownloadtable.otp_upload_manage.id)
            # ファイル名
            otp_upload_files = otpuploadmanage.file.all()
            files = []
            for file in otp_upload_files:         
                file_name = file.name + "\r\n"
                files.append(file_name)
            files = ' '.join(files)
            # files = otpuploadmanage.file.all()
            # ダウンロードテーブルの削除フラグを立てる
            otpdownloadtable.trash_flag = 1

            # その後保存する
            otpdownloadtable.save()
            # 操作ログ登録
            print('urlもしかしてfileみえない？3',files)
            # add_log(2,3,current_user,otp_delete_name,files,"",2,self.request.META.get('REMOTE_ADDR'))
            add_log(2,3,current_user,current_user.company,otp_delete_name,files,"",2,self.request.META.get('REMOTE_ADDR'))
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
# 受信テーブル ゲストアップロード 単数削除 #
##################################
class GuestDownloadTableDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        guest_delete_id = request.POST.get('guest_delete_id')
        guest_delete_name = request.POST.get('guest_delete_name')

        try:
            # ダウンロードテーブルに変更
            guestdownloadtable = GuestUploadDownloadtable.objects.get(pk__exact=guest_delete_id)
            print('げすと削除ここ？？？',guestdownloadtable)
            #↓二行操作ログ用・ファイル名取得
            guestuploadmanage = GuestUploadManage.objects.get(id=guestdownloadtable.guest_upload_manage.id)
            guest_upload_files = guestuploadmanage.file.all()
            files = []
            for file in guest_upload_files:         
                file_name = file.name + "\r\n"
                files.append(file_name)
            files = ' '.join(files)
            # ダウンロードテーブルの削除フラグを立てる
            guestdownloadtable.trash_flag = 1
            guestuploadmanage.file_del_flag = 1
            
            # その後保存する
            guestdownloadtable.save()
            guestuploadmanage.save()
            # 操作ログ登録
            add_log(2,3,current_user,current_user.company,guest_delete_name,files,"",6,self.request.META.get('REMOTE_ADDR'))
            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = guest_delete_name + 'を削除しました'
            return JsonResponse(data)

        except Exception as e:
            #失敗時のメッセージを格納してJASONで返す
            data = {}
            data['message'] = str(e)
            return JsonResponse(data)

##################################
# 受信テーブル一括削除 #
##################################
class MultiDownloadTableDeleteAjaxView(View,CommonView):
    def post(self, request,**kwargs):
        # print('一括削除かくにん繰り返してる？２２２２')
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        multi_delete_id = request.POST.getlist('dest_user_ids[]')#downloadテーブルのid(int)
        url_multi_delete_id = request.POST.getlist('url_dest_user_ids[]')
        otp_multi_delete_id = request.POST.getlist('otp_dest_user_ids[]')
        guest_multi_delete_id = request.POST.getlist('guest_dest_user_ids[]')
        print('ですとゆーざーにしてるのなんで1',multi_delete_id)
        print('ですとゆーざーにしてるのなんで2',url_multi_delete_id)
        print('ですとゆーざーにしてるのなんで3',otp_multi_delete_id)

        try:
            # ダウンロードテーブルに変更
            multi_tables = Downloadtable.objects.filter(pk__in=multi_delete_id)
            multi_tables = multi_tables.all()

            url_multi_tables = UrlDownloadtable.objects.filter(pk__in=url_multi_delete_id)
            url_multi_tables = url_multi_tables.all()
            
            otp_multi_tables = OTPDownloadtable.objects.filter(pk__in=otp_multi_delete_id)
            otp_multi_tables = otp_multi_tables.all()
            
            guest_multi_tables = GuestUploadDownloadtable.objects.filter(pk__in=guest_multi_delete_id)
            lst = [gtable for gtable in guest_multi_tables]
            guest_multi_manages = GuestUploadManage.objects.filter(pk__in=lst).all()
            guest_multi_tables = guest_multi_tables.all()
            #↓二行操作ログ用・ファイル名取得
            print('通常一括削除かくにん1',multi_tables)
            print('url一括削除かくにん1',url_multi_tables)
            print('otp一括削除かくにん1',otp_multi_tables)

            # ダウンロードテーブルに紐づいているファイルのQSを取得
            if multi_tables:
                for multi_table in multi_tables:
                    multi_table.trash_flag = 1
                    print('forの中マルチテーブル1',multi_table)
                    multi_table.save()
                    
            if url_multi_tables:
                for url_multi_table in url_multi_tables:
                    url_multi_table.trash_flag = 1
                    url_multi_table.save()
            
            elif otp_multi_tables:
                for otp_multi_table in otp_multi_tables:
                    otp_multi_table.trash_flag = 1
                    otp_multi_table.save()
            
            else:
                for guest_multi_table in guest_multi_tables:
                    guest_multi_table.trash_flag = 1

                    guest_multi_table.save()

                for guest_multi_manage in guest_multi_manages:
                    guest_multi_manage.file_del_flag = 1
                    guest_multi_manage.save()

            # 操作ログ登録-------操作ログには3レコード作成されてしまう。
            add_log(2,3,current_user,current_user.company,"","","",3,self.request.META.get('REMOTE_ADDR'))
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
            
            guest_download_tables = GuestUploadDownloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)
            guest_download_tables = guest_download_tables.all()

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
                
            for guest_download_table in guest_download_tables:
                guest_download_file_tables = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_download_table)
                files = guest_download_file_tables.all()

                guest_download_table.trash_flag = 0
                guest_download_table.save()

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
# ゲストアップロード ゴミ箱 単数削除  #
##################################
class GuestTrashDeleteAjaxView(View):
    def post(self, request):
        guest_delete_id = request.POST.get('guest_delete_id')
        guest_delete_name = request.POST.get('guest_delete_name')

        try:
            guestdownloadtable = GuestUploadDownloadtable.objects.get(pk__exact=guest_delete_id)
            guestdownloadtable.trash_flag = True
            guestdownloadtable.save()

            #メッセージを格納してJSONで返す
            data = {}
            data['message'] = guest_delete_name + 'を削除しました'
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
            guest_download_tables = GuestUploadDownloadtable.objects.filter(pk__in=deleted_ids, trash_flag=1)

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
            
            for guest_download_table in guest_download_tables:
                guest_download_file_tables = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_download_table)

                guest_download_table.trash_flag = 2
                guest_download_table.save()

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