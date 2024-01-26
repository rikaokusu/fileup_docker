from django.shortcuts import render
from django.views.generic import ListView, UpdateView, FormView, View, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import FileForm, ManageTasksStep1Form, DummyForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksUrlStep1Form, UrlDistFileUploadForm, UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, OTPDownloadtable, OTPDownloadFiletable, GuestUploadDownloadtable, GuestUploadDownloadFiletable, ResourceManagement, PersonalResourceManagement
from django.http import JsonResponse
from django.http import HttpResponse
import datetime
import urllib.parse
import zipfile
import io
from rest_framework import status

############################
# 一括(Zip)ダウンロード機能  #
############################
class FileDownloadZipView(View):

    def get(self, request, *args, **kwargs):
        # 対象課題のIDを取得
        pk = self.kwargs['pk']

        # ファイル情報を取得
        download_table = Downloadtable.objects.filter(pk=pk).first()
        downloadfiletable_qs = DownloadFiletable.objects.filter(download_table=download_table)

        # レスポンスの生成
        response = HttpResponse(content_type='application/zip')

        # ダウンロードするファイル名を定義
        fn_on_space = "download"

        # 半角スペース削除
        fn = fn_on_space.replace(" ", "")

        response['Content-Disposition'] = 'filename="{fn}.zip"'.format(fn=urllib.parse.quote(fn))

        # メモリーに保存する
        buffer = io.BytesIO()

        # Zipファイルの生成
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

        #dl_limitを取得する
        zip_dl_limit = download_table.upload_manage.dl_limit


        # Zipファイルに追加する
        for downloadfiletable in downloadfiletable_qs:
            file = downloadfiletable.download_file

            dl_file_count = downloadfiletable.dl_count
            if dl_file_count < zip_dl_limit:
                zip.writestr(file.name, file.upload.read())

        # Zipファイルをクローズ
        zip.close()

        # バッファのフラッシュ
        buffer.flush()

        # バッファの内容を書き出し
        ret_zip = buffer.getvalue()

        # バッファをクローズ
        buffer.close()

        # レスポンスに書き込み
        response.write(ret_zip)

        return response


################################
# URL共有 一括(Zip)ダウンロード機能  #
################################
class UrlFileDownloadZipView(View):

    def get(self, request, *args, **kwargs):
        # 対象課題のIDを取得
        pk = self.kwargs['pk']

        # ファイル情報を取得
        url_download_table = UrlDownloadtable.objects.filter(pk=pk).first()
        url_downloadfiletable_qs = UrlDownloadFiletable.objects.filter(url_download_table=url_download_table)

        # レスポンスの生成
        response = HttpResponse(content_type='application/zip')

        # ダウンロードするファイル名を定義
        fn_on_space = "download"

        # 半角スペース削除
        fn = fn_on_space.replace(" ", "")

        response['Content-Disposition'] = 'filename="{fn}.zip"'.format(fn=urllib.parse.quote(fn))

        # メモリーに保存する
        buffer = io.BytesIO()

        # Zipファイルの生成
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

        #dl_limitを取得する
        url_zip_dl_limit = url_download_table.url_upload_manage.dl_limit

        # Zipファイルに追加する
        for url_downloadfiletable in url_downloadfiletable_qs:
            file = url_downloadfiletable.download_file

            url_dl_file_count = url_downloadfiletable.url_dl_count
            if url_dl_file_count < url_zip_dl_limit:
                zip.writestr(file.name, file.upload.read())


        # Zipファイルをクローズ
        zip.close()

        # バッファのフラッシュ
        buffer.flush()

        # バッファの内容を書き出し
        ret_zip = buffer.getvalue()

        # バッファをクローズ
        buffer.close()

        # レスポンスに書き込み
        response.write(ret_zip)
        print("response.write(ret_zip)", ret_zip)

        return response

################################
# OTP 一括(Zip)ダウンロード機能  #
################################
class OTPFileDownloadZipView(View):

    def get(self, request, *args, **kwargs):
        # 対象課題のIDを取得
        pk = self.kwargs['pk']

        # ファイル情報を取得
        otp_download_table = OTPDownloadtable.objects.filter(pk=pk).first()
        otp_downloadfiletable_qs = OTPDownloadFiletable.objects.filter(otp_download_table=otp_download_table)

        # レスポンスの生成
        response = HttpResponse(content_type='application/zip')

        # ダウンロードするファイル名を定義
        fn_on_space = "download"

        # 半角スペース削除
        fn = fn_on_space.replace(" ", "")

        response['Content-Disposition'] = 'filename="{fn}.zip"'.format(fn=urllib.parse.quote(fn))

        # メモリーに保存する
        buffer = io.BytesIO()

        # Zipファイルの生成
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

        #dl_limitを取得する
        otp_zip_dl_limit = otp_download_table.otp_upload_manage.dl_limit

        # Zipファイルに追加する
        for otp_downloadfiletable in otp_downloadfiletable_qs:
            file = otp_downloadfiletable.download_file

            otp_dl_file_count = otp_downloadfiletable.otp_dl_count
            if otp_dl_file_count < otp_zip_dl_limit:
                zip.writestr(file.name, file.upload.read())


        # Zipファイルをクローズ
        zip.close()

        # バッファのフラッシュ
        buffer.flush()

        # バッファの内容を書き出し
        ret_zip = buffer.getvalue()

        # バッファをクローズ
        buffer.close()

        # レスポンスに書き込み
        response.write(ret_zip)
        print("response.write(ret_zip)", ret_zip)

        return response

################################
# ゲストアップロード 一括(Zip)ダウンロード機能  #
################################
class GuestFileDownloadZipView(View):
    
    def get(self, request, *args, **kwargs):
        print('ジップのはじまりにきた')
        # 対象課題のIDを取得
        pk = self.kwargs['pk']

        # ファイル情報を取得
        guest_download_table = GuestUploadDownloadtable.objects.filter(pk=pk).first()
        guest_downloadfiletable_qs = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_download_table)
        print('ジップの途中1')
        # レスポンスの生成
        response = HttpResponse(content_type='application/zip')

        # ダウンロードするファイル名を定義
        fn_on_space = "download"

        # 半角スペース削除
        fn = fn_on_space.replace(" ", "")

        response['Content-Disposition'] = 'filename="{fn}.zip"'.format(fn=urllib.parse.quote(fn))

        # メモリーに保存する
        buffer = io.BytesIO()
        print('ジップのメモリー保管済み')
        # Zipファイルの生成
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        print('ジップのファイル作成')

        # Zipファイルに追加する
        for guest_downloadfiletable in guest_downloadfiletable_qs:
            file = guest_downloadfiletable.download_file
            zip.writestr(file.name, file.upload.read())
        print('ジップのファイル追加')


        # Zipファイルをクローズ
        zip.close()

        # バッファのフラッシュ
        buffer.flush()

        # バッファの内容を書き出し
        ret_zip = buffer.getvalue()

        # バッファをクローズ
        buffer.close()

        # レスポンスに書き込み
        response.write(ret_zip)
        print("response.write(ret_zip)", ret_zip)
        print('ジップの終わり前')
        return response


######################################################
# ファイルダウンロード時にダウンロード管理テーブルを更新する処理  #
######################################################

class FileDownloadStatus(LoginRequiredMixin, View):
    # login_url = '/accounts/login/'

    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        is_type = request.POST.get('is_type')

        # downloadtableのidを呼び出す
        downloadtable_id = request.POST.get('downloadtable_id')

        # downloadtable_idからdownloadtableのオブジェクトを取得する
        downloadtable = Downloadtable.objects.filter(
            id=downloadtable_id).first()

        # downloadfiletableのQSを取得する。取得条件はdownloadtableが一致する行。
        downloadfiletable_qs = DownloadFiletable.objects.filter(download_table=downloadtable)

        # ファイルのIDをリスト化
        # file_idsの中身が単体と複数ファイルの場合の条件定義
        file_ids = []
        if is_type == "single":
            file_ids.append(request.POST.get('file_id'))
        elif is_type == "multiple":
            for file in downloadfiletable_qs.all():
                file_ids.append(file.download_file.id)

        else:
            pass

        try:
            for file_id in file_ids:
                # ファイルIDからファイルモデルのオブジェクトを取得する
                filemodel = Filemodel.objects.filter(id=file_id).first()

                downloadfiletable = DownloadFiletable.objects.filter(download_table=downloadtable, download_file=filemodel).first()

                # 取得したDownloadFiletableのオブジェクトのis_downloadedの値をTrueに変更する
                downloadfiletable.is_downloaded = True
                downloadfiletable.dl_count += 1

                # DownloadFiletableのオブジェクトを保存する"""
                # downloadfiletable.save()

                # ダウンロード時間を保持して保存する
                downloadfiletable.dowloaded_date = datetime.datetime.now()
                downloadfiletable.save()

                downloadtable.dowloaded_date = datetime.datetime.now()
                downloadtable.save()

            # ユーザー個別のDL状況
            # ダウンロードファイルテーブルで受信テーブルに紐づいている全ての行を取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            file_number = DownloadFiletable.objects.filter(download_table=downloadtable).count()

            # ダウンロードファイルテーブルで受信テーブルに紐づいている中で、is_downloadedフラグがTrueのものを取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            downloaded_file_number = DownloadFiletable.objects.filter(download_table=downloadtable, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                downloadtable.is_downloaded = True  # 対応完了

                downloadtable.save()

            # DownloadtableでUploadManageに紐づいている行を取得

            file_number = Downloadtable.objects.filter(upload_manage=downloadtable.upload_manage).count()
            downloaded_file_number = Downloadtable.objects.filter(upload_manage=downloadtable.upload_manage, is_downloaded=True).count()

            if file_number == downloaded_file_number:
                downloadtable.upload_manage.is_downloaded = True  # 対応完了

            downloadtable.upload_manage.save()


        except Exception as e:
            return JsonResponse({"status": "ng",
                                "message": str(e),
                                })

        return JsonResponse({"status": "ok",
                            "message": "ダウンロードしました",
                            })

######################################################
# URL共有　ファイルダウンロード時にダウンロード管理テーブルを更新する処理  #
######################################################

class UrlFileDownloadStatus(LoginRequiredMixin, View):

    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        is_type = request.POST.get('is_type')

        # downloadtableのidを呼び出す
        url_downloadtable_id = request.POST.get('url_downloadtable_id')

        # downloadtable_idからdownloadtableのオブジェクトを取得する
        url_downloadtable = UrlDownloadtable.objects.filter(id=url_downloadtable_id).first()

        # downloadfiletableのQSを取得する。取得条件はdownloadtableが一致する行。
        url_downloadfiletable_qs = UrlDownloadFiletable.objects.filter(url_download_table=url_downloadtable)

        # ファイルのIDをリスト化
        # file_idsの中身が単体と複数ファイルの場合の条件定義
        file_ids = []
        if is_type == "single":
            file_ids.append(request.POST.get('file_id'))
        elif is_type == "multiple":
            for file in url_downloadfiletable_qs.all():
                file_ids.append(file.download_file.id)

        else:
            pass

        try:
            for file_id in file_ids:
                # ファイルIDからファイルモデルのオブジェクトを取得する
                filemodel = Filemodel.objects.filter(id=file_id).first()

                urL_downloadfiletable = UrlDownloadFiletable.objects.filter(url_download_table=url_downloadtable, download_file=filemodel).first()
                # 取得したDownloadFiletableのオブジェクトのis_downloadedの値をTrueに変更する
                urL_downloadfiletable.is_downloaded = True
                urL_downloadfiletable.url_dl_count += 1


                # DownloadFiletableのオブジェクトを保存する"""
                urL_downloadfiletable.save()

                # ダウンロード時間を保持して保存する
                urL_downloadfiletable.dowloaded_date = datetime.datetime.now()
                urL_downloadfiletable.save()

                urL_downloadfiletable.dowloaded_date = datetime.datetime.now()
                urL_downloadfiletable.save()

            # ユーザー個別のDL状況
            # ダウンロードファイルテーブルで受信テーブルに紐づいている全ての行を取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            file_number = UrlDownloadFiletable.objects.filter(url_download_table=url_downloadtable).count()

            # ダウンロードファイルテーブルで受信テーブルに紐づいている中で、is_downloadedフラグがTrueのものを取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            downloaded_file_number = UrlDownloadFiletable.objects.filter(url_download_table=url_downloadtable, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                url_downloadtable.is_downloaded = True  # 対応完了

                url_downloadtable.save()

            # DownloadtableでUploadManageに紐づいている行を取得

            file_number = UrlDownloadtable.objects.filter(url_upload_manage=url_downloadtable.url_upload_manage).count()

            downloaded_file_number = UrlDownloadtable.objects.filter(url_upload_manage=url_downloadtable.url_upload_manage, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                url_downloadtable.url_upload_manage.is_downloaded = True  # 対応完了

                url_downloadtable.url_upload_manage.save()

        except Exception as e:
            return JsonResponse({"status": "ng",
                                "message": str(e),
                                })

        return JsonResponse({"status": "ok",
                            "message": "ダウンロードしました",
                            })


######################################################
# OTP　ファイルダウンロード時にダウンロード管理テーブルを更新する処理  #
######################################################

class OTPFileDownloadStatus(LoginRequiredMixin, View):

    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        is_type = request.POST.get('is_type')

        # downloadtableのidを呼び出す
        otp_downloadtable_id = request.POST.get('otp_downloadtable_id')

        # downloadtable_idからdownloadtableのオブジェクトを取得する
        otp_downloadtable = OTPDownloadtable.objects.filter(id=otp_downloadtable_id).first()

        # downloadfiletableのQSを取得する。取得条件はdownloadtableが一致する行。
        otp_downloadfiletable_qs = OTPDownloadFiletable.objects.filter(otp_download_table=otp_downloadtable)

        # ファイルのIDをリスト化
        # file_idsの中身が単体と複数ファイルの場合の条件定義
        file_ids = []
        if is_type == "single":
            file_ids.append(request.POST.get('file_id'))
        elif is_type == "multiple":
            for file in otp_downloadfiletable_qs.all():
                file_ids.append(file.download_file.id)

        else:
            pass

        try:
            for file_id in file_ids:
                # ファイルIDからファイルモデルのオブジェクトを取得する
                filemodel = Filemodel.objects.filter(id=file_id).first()

                otp_downloadfiletable = OTPDownloadFiletable.objects.filter(otp_download_table=otp_downloadtable, download_file=filemodel).first()
                # 取得したDownloadFiletableのオブジェクトのis_downloadedの値をTrueに変更する
                otp_downloadfiletable.is_downloaded = True
                otp_downloadfiletable.otp_dl_count += 1


                # DownloadFiletableのオブジェクトを保存する"""
                otp_downloadfiletable.save()

                # ダウンロード時間を保持して保存する
                otp_downloadfiletable.dowloaded_date = datetime.datetime.now()
                otp_downloadfiletable.save()

                otp_downloadfiletable.dowloaded_date = datetime.datetime.now()
                otp_downloadfiletable.save()

            # ユーザー個別のDL状況
            # ダウンロードファイルテーブルで受信テーブルに紐づいている全ての行を取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            file_number = OTPDownloadFiletable.objects.filter(otp_download_table=otp_downloadtable).count()

            # ダウンロードファイルテーブルで受信テーブルに紐づいている中で、is_downloadedフラグがTrueのものを取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            downloaded_file_number = OTPDownloadFiletable.objects.filter(otp_download_table=otp_downloadtable, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                otp_downloadtable.is_downloaded = True  # 対応完了

                otp_downloadtable.save()

            # DownloadtableでUploadManageに紐づいている行を取得

            file_number = OTPDownloadtable.objects.filter(otp_upload_manage=otp_downloadtable.otp_upload_manage).count()

            downloaded_file_number = OTPDownloadtable.objects.filter(otp_upload_manage=otp_downloadtable.otp_upload_manage, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                otp_downloadtable.otp_upload_manage.is_downloaded = True  # 対応完了

                otp_downloadtable.otp_upload_manage.save()

        except Exception as e:
            return JsonResponse({"status": "ng",
                                "message": str(e),
                                })

        return JsonResponse({"status": "ok",
                            "message": "ダウンロードしました",
                            })

######################################################
# ゲストアップロード　ファイルダウンロード時にダウンロード管理テーブルを更新する処理  #
######################################################

class GuestFileDownloadStatus(LoginRequiredMixin, View):

    def post(self, request):

        # ダウンロードされたファイルが単体か複数か判断するための変数
        is_type = request.POST.get('is_type')

        # downloadtableのidを呼び出す
        guest_downloadtable_id = request.POST.get('guest_downloadtable_id')

        # downloadtable_idからdownloadtableのオブジェクトを取得する
        guest_downloadtable = GuestUploadDownloadtable.objects.filter(id=guest_downloadtable_id).first()

        # downloadfiletableのQSを取得する。取得条件はdownloadtableが一致する行。
        guest_downloadfiletable_qs = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_downloadtable)

        # ファイルのIDをリスト化
        # file_idsの中身が単体と複数ファイルの場合の条件定義
        file_ids = []
        if is_type == "single":
            file_ids.append(request.POST.get('file_id'))
        elif is_type == "multiple":
            for file in guest_downloadfiletable_qs.all():
                file_ids.append(file.download_file.id)

        else:
            pass

        try:
            for file_id in file_ids:
                # ファイルIDからファイルモデルのオブジェクトを取得する
                filemodel = Filemodel.objects.filter(id=file_id).first()

                guest_downloadfiletable = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_downloadtable, download_file=filemodel).first()
                # 取得したDownloadFiletableのオブジェクトのis_downloadedの値をTrueに変更する
                guest_downloadfiletable.is_downloaded = True
                guest_downloadfiletable.guest_upload_dl_count += 1


                # DownloadFiletableのオブジェクトを保存する"""
                guest_downloadfiletable.save()

                # ダウンロード時間を保持して保存する
                guest_downloadfiletable.dowloaded_date = datetime.datetime.now()
                guest_downloadfiletable.save()

                guest_downloadfiletable.dowloaded_date = datetime.datetime.now()
                guest_downloadfiletable.save()

            # ユーザー個別のDL状況
            # ダウンロードファイルテーブルで受信テーブルに紐づいている全ての行を取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            file_number = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_downloadtable).count()

            # ダウンロードファイルテーブルで受信テーブルに紐づいている中で、is_downloadedフラグがTrueのものを取得
            # 最後に.count()をつけて、QSの数がint型で返ってくるようにする。
            downloaded_file_number = GuestUploadDownloadFiletable.objects.filter(guest_upload_download_table=guest_downloadtable, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                guest_downloadtable.is_downloaded = True  # 対応完了

                guest_downloadtable.save()

            # DownloadtableでUploadManageに紐づいている行を取得

            file_number = GuestUploadDownloadtable.objects.filter(guest_upload_manage=guest_downloadtable.guest_upload_manage).count()

            downloaded_file_number = GuestUploadDownloadtable.objects.filter(guest_upload_manage=guest_downloadtable.guest_upload_manage, is_downloaded=True).count()

            if file_number == downloaded_file_number:

                guest_downloadtable.guest_upload_manage.is_downloaded = True  # 対応完了

                guest_downloadtable.guest_upload_manage.save()

        except Exception as e:
            return JsonResponse({"status": "ng",
                                "message": str(e),
                                })

        return JsonResponse({"status": "ok",
                            "message": "ダウンロードしました",
                            })
