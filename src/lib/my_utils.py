from accounts.models import User
from datetime import datetime,timezone
from django.contrib import messages
from django.shortcuts import redirect
from draganddrop.models import OperationLog


import logging
logger = logging.getLogger(__name__)

def check_session(self, request, instance):


    # GET時のみ動作
    if request.method == "GET":

        # 変更フラグの存在を確認
        if instance.version:
            id = str(instance.id)

            # 自分自身の場合
            if instance.change_user == str(self.request.user.id):
                messages.error(request, '変更中のセッションが残っています。セッションを破棄して新たに変更しますか？<div type="button" id="okBtn" data-id=' + '"' + id + '"' + ' data-url="update_profile" class="my-btn my-btn-egypt-1 my-btn-s my-btn-w5 ml-1 mr-1">はい</div><div type="button" data-url="update_profile" class="my-btn my-btn-gray-1 my-btn-s my-btn-w5 ml-1 mr-1">いいえ</div>')
                return redirect('accounts:companyprofile')

            # 他ユーザの場合
            else:
                user = User.objects.filter(id=instance.change_user).first()

                change_user = str(user.display_name)

                timestamp = instance.version
                now = datetime.now(timezone.utc)

                diff = now - timestamp

                # 30分以上立っている場合
                if diff.seconds >= 1800:

                    messages.error(request, '' + change_user + ' さんが変更中です。セッションを破棄して新たに変更しますか？<div type="button" id="okBtn" data-id=' + '"' + id + '"' + ' data-url="update_profile" class="my-btn my-btn-egypt-1 my-btn-s my-btn-w5 ml-1 mr-1">はい</div><div type="button" data-url="update_profile" class="my-btn my-btn-gray-1 my-btn-s my-btn-w5 ml-1 mr-1">いいえ</div>')
                    return redirect('accounts:companyprofile')

                # 30分未満の場合
                else:
                    messages.error(request, '' + change_user + ' さんが変更中です。<div type="button" id="okBtn" class="my-btn my-btn-gray-1 my-btn-s my-btn-w5 ml-1 mr-1">閉じる</div>')
                    return redirect('accounts:companyprofile')


        else:
            # 変更フラグをセット
            instance.version = datetime.now()
            # 変更者のIDをセット
            instance.change_user =  self.request.user.id
            # 保存
            instance.save()

def add_log(operation, category, op_user,log_filename,upload_category, client_addr):

    logger.debug("operation")
    logger.debug(operation)
    logger.debug("category")
    logger.debug(category)
    logger.debug("op_user")
    logger.debug(op_user)
    logger.debug("upload_category")
    logger.debug(upload_category)

    operation_log_obj = OperationLog.objects.create(
        created_date = datetime.now(),
        operation_user = op_user,
        category = category,
        operation = operation,
        log_filename = log_filename,
        upload_category = upload_category,
        client_addr = client_addr,
    )