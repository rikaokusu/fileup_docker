from django.urls import path, include
from .views.home import send_table, download_table, home_common, file_download, url_access, otp_access
from .views.admin import admin_personal, admin_company,log
from .views.recipient import address, group
from .views.approval import approval
from .views.upload import upload, url_share, duplicate, upload_common, otp_upload, guest_upload
from django.contrib.auth import views as auth_views

app_name = 'draganddrop'

urlpatterns = [

     ############
     # home  #
     ############
     ## home_common.py ##
     # ホーム(トップ)画面 
     path('', home_common.FileuploadListView.as_view(), name='home'),

     ## url_access ##
     path('url_check/<str:token>/', url_access.ApproveView.as_view(), name='approve'),
     path('url_file_download_auth_mail/<uuid:pk>', url_access.UrlFileDownloadAuthMail.as_view(), name='url_file_download_auth_mail'),
     path('url_file_download_auth_pass/<uuid:pk>',url_access.UrlFileDownloadAuthPass.as_view(), name='url_file_download_auth_pass'),
     path('url_file_download/<uuid:pk>',url_access.UrlFileDownload.as_view(), name='url_file_download'),
     path('url_file_unable_download/', url_access.UrlFileUnableDownload.as_view(),name='url_file_unable_download'),
     
     ## otp ##
     path('otp_check/<str:token>/', otp_access.OTPApproveView.as_view(), name='otpapprove'),
     path('otp_file_download_auth/<uuid:pk>', otp_access.OTPFileDownloadAuth.as_view(), name='otp_file_download_auth'),
     path('otp_file_download/<uuid:pk>', otp_access.OTPFileDownload.as_view(), name='otp_file_download'),
     path('otp_file_unable_download/', otp_access.OTPFileUnableDownload.as_view(),name='otp_file_unable_download'),
     path('otp_send/', otp_access.OTPSendAjaxView.as_view(),name='otp_send'),
     
     ## file_download.py ##
     # 一括ダウンロード
     path('file_download_zip/<int:pk>/', file_download.FileDownloadZipView.as_view(), name='file_download_zip'),
     path('url_file_download_zip/<int:pk>/', file_download.UrlFileDownloadZipView.as_view(), name='url_file_download_zip'),
     path('otp_file_download_zip/<int:pk>/', file_download.OTPFileDownloadZipView.as_view(), name='otp_file_download_zip'),
     path('guest_file_download_zip/<int:pk>/', file_download.GuestFileDownloadZipView.as_view(), name='guest_file_download_zip'),

     # ファイルダウンロード時にテーブルを更新する処理
     path('filedownloadstatus/', file_download.FileDownloadStatus.as_view(), name='filedownloadstatus'),
     path('url_file_download_status/', file_download.UrlFileDownloadStatus.as_view(), name='url_file_download_status'),
     path('otp_file_download_status/', file_download.OTPFileDownloadStatus.as_view(), name='otp_file_download_status'),
     path('guest_file_download_status/', file_download.GuestFileDownloadStatus.as_view(), name='guest_file_download_status'),

     ## send_table.py ##
     # 送信テーブルファイルアップロード単数削除 ☑
     path('delete/', send_table.DeleteAjaxView.as_view(), name='delete'),
     # 送信テーブルのファイルアップロード ファイルのみ削除 ☑
     path('file_delete/', send_table.FileDeleteAjaxView.as_view(), name='file_delete'),
     # 送信テーブル URL共有単数削除  
     path('url_delete/', send_table.UrlDeleteAjaxView.as_view(), name='url_delete'),
     # 送信テーブルのURL共有 ファイルのみ削除 
     path('url_file_delete/', send_table.UrlFileDeleteAjaxView.as_view(), name='url_file_delete'),
     # 送信テーブル OTP単数削除  
     path('otp_delete/', send_table.OTPDeleteAjaxView.as_view(), name='otp_delete'),
     # 送信テーブルのOTP ファイルのみ削除 
     path('otp_file_delete/', send_table.OTPFileDeleteAjaxView.as_view(), name='otp_file_delete'),
     # 送信テーブルの一括削除 
     path('send_table_multi_delete/', send_table.SendTableMultiDeleteAjaxView.as_view(), name='send_table_multi_delete'),
     # 送信テーブル ファイルのみ一括削除
     path('send_table_file_multi_delete/', send_table.SendTableFileMultiDeleteAjaxView.as_view(), name='send_table_file_multi_delete'),

     ## download_table.py ##
     # 受信テーブル ファイルアップロード単数削除(ゴミ箱へ)
     path('downloadtabledelete/', download_table.DownloadTableDeleteAjaxView.as_view(), name='downloadtabledelete'),
     # 受信テーブル URL共有単数削除(ゴミ箱へ)
     path('urldownloadtabledelete/', download_table.UrlDownloadTableDeleteAjaxView.as_view(), name='urldownloadtabledelete'),
     # 受信テーブル OTP単数削除(ゴミ箱へ)
     path('otpdownloadtabledelete/', download_table.OTPDownloadTableDeleteAjaxView.as_view(), name='otpdownloadtabledelete'),
     # 受信テーブル ゲストアップロード単数削除(ゴミ箱へ)
     path('guestdownloadtabledelete/', download_table.GuestDownloadTableDeleteAjaxView.as_view(), name='guestdownloadtabledelete'),
     # 受信テーブル 一括削除(ゴミ箱へ)  
     path('multi_dl_delete/', download_table.MultiDownloadTableDeleteAjaxView.as_view(), name='multi_dl_delete'),
     # ゴミ箱 復元 
     path('restore/', download_table.RestoreAjaxView.as_view(), name='restore'),
     # ゴミ箱 単数削除
     path('trashdelete/', download_table.TrashDeleteAjaxView.as_view(), name='trashdelete'),
     # ゴミ箱 URL共有 単数削除
     path('urltrashdelete/', download_table.UrlTrashDeleteAjaxView.as_view(),name='urltrashdelete'),
     # ゴミ箱 OTP 単数削除
     path('otptrashdelete/', download_table.OTPTrashDeleteAjaxView.as_view(),name='otptrashdelete'),
     # ゴミ箱 ゲストアップロード 単数削除
     path('guesttrashdelete/', download_table.GuestTrashDeleteAjaxView.as_view(),name='guesttrashdelete'),
     # ゴミ箱 一括削除
     path('multidelete/', download_table.MultiDeleteAjaxView.as_view(), name='multidelete'),
     

     # """
     # お知らせ
     # """
     path('infomation/<uuid:pk>', home_common.InfomationView.as_view(), name='information'),

     ############################
     #  ユーザープロフィール情報変更
     path('update_userinfomation/<uuid:pk>', home_common.UserUpdateInfoView.as_view(), name='update_userinfomation'),

     #現在の写真削除
     path('accounts/delete_image/', home_common.delete_image, name='delete_image'),
     #ユーザープロファイル画像変更
     path('user/image_import/', home_common.ImageImportView.as_view(), name='image_import'),

     # upload  ファイルアップロード、URL共有、複製 #
     ##########################################    
     ## upload.py ##
     # ファイルアップロード(追加) 
     path('step1/', upload.Step1.as_view(), name='step1'),
     path('step2/<uuid:pk>', upload.Step2.as_view(), name='step2'),
     path('step3/<uuid:pk>', upload.Step3.as_view(), name='step3'),
     path('return/<uuid:pk>', upload.ReturnView.as_view(), name='return'),

     # ファイルアップロード(変更)
     path('step1_update/<uuid:pk>', upload.Step1Update.as_view(), name='step1_update'),
     path('step2_update/<uuid:pk>', upload.Step2Update.as_view(), name='step2_update'),
     path('step3_update/<uuid:pk>', upload.Step3Update.as_view(), name='step3_update'),
     path('return_update/<uuid:pk>',upload.ReturnUpdateView.as_view(), name='return_update'),

     ## url_share.py ##
     # URL共有(追加)
     path('step1_url_upload/', url_share.Step1UrlUpload.as_view(), name='step1_url_upload'),
     path('step2_url_upload/<uuid:pk>', url_share.Step2URLupload.as_view(), name='step2_url_upload'),
     path('step3_url_upload/<uuid:pk>', url_share.Step3URLupload.as_view(), name='step3_url_upload'),
     path('url_return/<uuid:pk>', url_share.UrlReturnView.as_view(), name='url_return'),

     # URL共有(変更) 
     path('url_upload_manage_id/<uuid:pk>', url_share.Step1UrlUpdate.as_view(), name='step1_url_update'),
     path('step2_url_update/<uuid:pk>', url_share.Step2UrlUpdate.as_view(), name='step2_url_update'),
     path('step3_url_update/<uuid:pk>', url_share.Step3UrlUpdate.as_view(), name='step3_url_update'),
     path('url_return_update/<uuid:pk>',url_share.UrlReturnUpdateView.as_view(), name='url_return_update'),
     
     ## otp_upload.py ##
     # OTPアップロード(追加)
     path('step1_otp_upload/', otp_upload.Step1OTPUpload.as_view(), name='step1_otp_upload'),
     path('step2_otp_upload/<uuid:pk>', otp_upload.Step2OTPupload.as_view(), name='step2_otp_upload'),
     path('step3_otp_upload/<uuid:pk>', otp_upload.Step3OTPupload.as_view(), name='step3_otp_upload'),
     path('otp_return/<uuid:pk>', otp_upload.OTPReturnView.as_view(), name='otp_return'),

     # OTPアップロード(変更) 
     path('otp_upload_manage_id/<uuid:pk>', otp_upload.Step1OTPUpdate.as_view(), name='step1_otp_update'),
     path('step2_otp_update/<uuid:pk>', otp_upload.Step2OTPUpdate.as_view(), name='step2_otp_update'),
     path('step3_otp_update/<uuid:pk>', otp_upload.Step3OTPUpdate.as_view(), name='step3_otp_update'),
     path('otp_return_update/<uuid:pk>',otp_upload.OTPReturnUpdateView.as_view(), name='otp_return_update'),
     
      ## guest_upload.py ##
     # ゲストアップロード(作成・リクエスト)
     path('step1_guest_upload_create/', guest_upload.Step1GuestUploadCreate.as_view(), name='step1_guest_upload_create'),
     path('step2_guest_upload_create/<uuid:pk>', guest_upload.Step2GuestUploadCreate.as_view(), name='step2_guest_upload_create'),
    #  path('guest_upload_return/<uuid:pk>', guest_upload.GuestReturnView.as_view(), name='guest_return'),
     # ゲストアップロード(作成・リクエスト変更) 
    #  path('otp_upload_manage_id/<uuid:pk>', otp_upload.Step1OTPUpdate.as_view(), name='step1_otp_update'),
    #  path('step2_otp_update/<uuid:pk>', otp_upload.Step2OTPUpdate.as_view(), name='step2_otp_update'),
    #  path('step3_otp_update/<uuid:pk>', otp_upload.Step3OTPUpdate.as_view(), name='step3_otp_update'),
     # ゲストアップロード（ファイルアップロード）
     path('guest_check/<str:token>/', guest_upload.GuestApproveView.as_view(), name='guestapprove'),
     path('guest_file_upload_auth/<uuid:pk>', guest_upload.GuestFileUploadAuth.as_view(), name='guest_file_upload_auth'),
     path('guest_send/', guest_upload.GuestSendAjaxView.as_view(),name='guest_send'),
     path('step1_guest_upload/<uuid:pk>', guest_upload.Step1GuestUpload.as_view(), name='step1_guest_upload'),
     path('step2_guest_upload/<uuid:pk>', guest_upload.Step2GuestUpload.as_view(), name='step2_guest_upload'),
     path('guest_file_unable_upload/', guest_upload.GuestFileUnableUpload.as_view(),name='guest_file_unable_upload'),
    

     ## duplicate.py ##
     # ファイルアップロード(複製)  
     path('duplicate_step1/<uuid:pk>', duplicate.DuplicateStep1.as_view(), name='duplicate_step1'),
     path('duplicate_step2/<uuid:pk>', duplicate.DuplicateStep2.as_view(), name='duplicate_step2'),
     path('duplicate_step3/<uuid:pk>', duplicate.DuplicateStep3.as_view(), name='duplicate_step3'),
     path('duplicate_return/<uuid:pk>', duplicate.DuplicateReturnView.as_view(), name='duplicate_return'),

     # URL共有(複製) 
     path('url_duplicate_step1/<uuid:pk>', duplicate.UrlDuplicateStep1.as_view(), name='url_duplicate_step1'),
     path('url_duplicate_step2/<uuid:pk>', duplicate.UrlDuplicateStep2.as_view(), name='url_duplicate_step2'),
     path('url_duplicate_step3/<uuid:pk>', duplicate.UrlDuplicateStep3.as_view(), name='url_duplicate_step3'),
     path('url_duplicate_return/<uuid:pk>', duplicate.UrlDuplicateReturnView.as_view(), name='url_duplicate_return'),
     
     # OTPアップロード(複製) 
     path('otp_duplicate_step1/<uuid:pk>', duplicate.OTPDuplicateStep1.as_view(), name='otp_duplicate_step1'),
     path('otp_duplicate_step2/<uuid:pk>', duplicate.OTPDuplicateStep2.as_view(), name='otp_duplicate_step2'),
     path('otp_duplicate_step3/<uuid:pk>', duplicate.OTPDuplicateStep3.as_view(), name='otp_duplicate_step3'),
     path('otp_duplicate_return/<uuid:pk>', duplicate.OTPDuplicateReturnView.as_view(), name='otp_duplicate_return'),
     
     ## upload_common.py ##
     # キャンセル機能
     path('cancel/', upload_common.CancelView.as_view(), name='cancel'),
     # Filemodelオブジェクト作成
     path('file_upload/', upload_common.FileUpload.as_view(), name='file_upload'),
     path('guest_file_upload/', upload_common.GuestFileUpload.as_view(), name='guest_file_upload'),
     # Dropzone アップロードファイルの削除 
     path('dropzonefiledelete/', upload_common.DropZoneFileDeleteView.as_view(),name='dropzonefiledelete'),

     ####################################
     # recipient  アドレス帳、グループ登録 #
     ####################################  
     
     ## address.py ##
     # ユーザー一覧
     path('address_list/', address.AddressListView.as_view(), name='address_list'),
     # 変更時のデータ取得
     path('get_update_address_modal/<int:pk>/', address.GetUpdateModalAjaxView.as_view(), name='get_update_address_modal'),
     # ユーザー登録
     path('address_update/<int:pk>/', address.UpdateAddressAjaxView.as_view(), name='address_update'),
     # ユーザー単数削除
     path('address_delete/', address.AddressDeleteAjaxView.as_view(), name='address_delete'),
     # ユーザー一括削除
     path('address_multi_delete/', address.AddressMultiDeleteAjaxView.as_view(), name='address_multi_delete'),
     # アドレスバリデーション
     path('address_email_validation/', address.AddressEmailValidationView.as_view(), name='address_email_validation'),

     ## group.py ## 
     # グループ一覧
     path('group_list/', group.GroupListView.as_view(), name='group_list'),
     # グループ登録
     path('group_create/', group.GroupCreateAjaxView.as_view(), name='group_create'),
     # グループ名バリデーション
     path('group_name_validation/', group.GroupNameValidationView.as_view(), name='group_name_validation'),
     # グループ変更時のデータ取得
     path('get_group_update_address_modal/<int:pk>/', group.GetGroupUpdateModalAjaxView.as_view(), name='get_group_update_address_modal'),
     # グループ変更
     path('group_update/', group.GroupUpdateAjaxView.as_view(), name='group_update'),
     # グループ削除
     path('group_delete/', group.GroupDeleteAjaxView.as_view(), name='group_delete'),
     # グループ一括削除
     path('group_multi_delete/', group.GroupMultiDeleteAjaxView.as_view(), name='group_multi_delete'),

     
     ##################################
     # admin ディスク容量管理  
     ##################################
     ## admin_company.py 会社のリソース管理 ##
     path('resource_management/', admin_company.ResourceManagementView.as_view(), name='resource_management'),
     ## admin_personal.py 個人のリソース管理 ##
     path('personal_resource_management/', admin_personal.PersonalResourceManagementView.as_view(), name='personal_resource_management'),


     ##################################
     # 承認ワークフロー 
     ##################################
     # 基本設定(承認一覧)
     path('approval_workflow/', approval.ApprovalWorkflowView.as_view(), name='approval_workflow'),
     # 基本設定(申請一覧)
     # path('application_workflow/', approval.ApplicationView.as_view(), name='application_workflow'),
     # 基本設定 編集画面
     path('approval_workflow_edit/<uuid:pk>/', approval.ApprovalWorkflowEditView.as_view(), name='approval_workflow_edit'),
     # 第一承認者設定
     path('first_approver_set/', approval.FirstApproverSetView.as_view(), name='first_approver_set'),
     # 第一承認者の個別削除
     path('first_approver_delete/<uuid:pk>/',approval.FirstApproverDeleteView.as_view(),name='first_approver_delete'),
     # 第二承認者設定
     path('second_approver_set/', approval.SecondApproverSetView.as_view(), name='second_approver_set'),
     # 第二承認者の個別削除
     path('second_approver_delete/<uuid:pk>/',approval.SecondApproverDeleteView.as_view(),name='second_approver_delete'),
     # 操作ログ
     path('approval_log/', approval.ApprovalLogView.as_view(), name='approval_log'),
     # 承認詳細
     path('approval_detail/<uuid:pk>/', approval.ApprovalDetailView.as_view(), name='approval_detail'),

     # 承認
     path('approve/<uuid:pk>/', approval.ApproveView.as_view(), name='approve'),
     # 差戻し
     path('returned_application/<uuid:pk>/', approval.DeclineApplicationView.as_view(), name='returned_application'),
     # 再申請
     path('reapplication/<uuid:pk>/', approval.ReapplicationView.as_view(), name='reapplication'),
     # 取り消し(削除) 通常アップロードアップロード
     path('approvaldelete/', approval.ApprovalDeleteAjaxView.as_view(), name='approvaldelete'),
     # 取り消し(削除) URL共有
     path('urlapprovaldelete/', approval.UrlApprovalDeleteAjaxView.as_view(), name='urlapprovaldelete'),
     # 取り消し(削除) OPT共有
     path('optapprovaldelete/', approval.OTPApprovalDeleteAjaxView.as_view(), name='optapprovaldelete'),

     ##################################
     # 操作ログ  
     ##################################
     path('log/', log.LogView.as_view(), name='log'),
]
