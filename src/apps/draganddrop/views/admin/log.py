from django.shortcuts import render
from datetime import datetime,timezone
from django.views.generic import TemplateView
from draganddrop.views.home.home_common import CommonView
from draganddrop.models import OperationLog
from accounts.models import FileupPermissions
# import logging
# logger = logging.getLogger(__name__)

# """
# 操作ログ関数
# """
# def add_log(operation, category, op_user,log_filename,upload_category, client_addr):

#     logger.debug("operation")
#     logger.debug(operation)
#     logger.debug("category")
#     logger.debug(category)
#     logger.debug("op_user")
#     logger.debug(op_user)
#     logger.debug("upload_category")
#     logger.debug(upload_category)

#     operation_log_obj = OperationLog.objects.create(
#         created_date = datetime.now(),
#         operation_user = op_user,
#         category = category,
#         operation = operation,
#         log_filename = log_filename,
#         upload_category = upload_category,
#         client_addr = client_addr,
#     )
"""
操作ログ画面
"""
class LogView(CommonView,TemplateView):
    # model = User
    template_name = 'draganddrop/log.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        user_permission = FileupPermissions.objects.get(user=current_user)

        #管理者(社内の人見れる)
        if user_permission.permission >= "1":
            logs =  OperationLog.objects.filter(operation_user_company_id=current_user.company,category=2)
            guest_logs =  OperationLog.objects.filter(operation_user_company_id=current_user.company,upload_category=6,category=2)
            logs = logs.union(guest_logs).order_by('created_date').reverse
        elif user_permission.permission == "0": #一般ユーザー（自分しか見れない）
            logs =  OperationLog.objects.filter(operation_user=current_user,category=2)
            guest_logs =  OperationLog.objects.filter(upload_category=6,category=2,destination_address=current_user.email)
            logs = logs.union(guest_logs).order_by('created_date').reverse



        print('ゲストのレコードわかる？？？？？？？？？？',guest_logs)

        logs_address_user =  OperationLog.objects.filter(operation_user=current_user,category=3,upload_category=4).order_by('created_date').reverse
        logs_address_group =  OperationLog.objects.filter(operation_user=current_user,category=3,upload_category=5).order_by('created_date').reverse
        # log_files =  LogFile.objects.all()
        # log_destusers = LogDestUser.objects.all()
        logsfirst =  OperationLog.objects.first()
        print('ろぐですーーーーーーー',logs)
        print('ろぐですーーーーーーー',logsfirst)

        context['logs'] = logs
        context['logs_address_user'] = logs_address_user
        context['logs_address_group'] = logs_address_group
        context['logsfirst'] = logsfirst
        # context['log_files'] = log_files
        # context['log_destusers'] = log_destusers
        
        return context
