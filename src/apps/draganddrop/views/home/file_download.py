from django.shortcuts import render
from django.views.generic import ListView, UpdateView, FormView, View, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...forms import FileForm, ManageTasksStep1Form, DummyForm, DistFileUploadForm, AddressForm, GroupForm, ManageTasksUrlStep1Form, UrlDistFileUploadForm, UrlFileDownloadAuthMailForm, UrlFileDownloadAuthPassForm
from draganddrop.models import Filemodel, UploadManage, PDFfilemodel, Downloadtable, DownloadFiletable, Address, Group, UrlUploadManage, UrlDownloadtable, UrlDownloadFiletable, ResourceManagement, PersonalResourceManagement
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
# ファイルダウンロード時にダウンロード管理テーブルを更新する処理  #
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
