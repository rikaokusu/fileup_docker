from django.shortcuts import render
from datetime import datetime,timezone
from django.views.generic import TemplateView
from draganddrop.views.home.home_common import CommonView
from draganddrop.models import OperationLog,LogFile,LogDestUser
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
        logs =  OperationLog.objects.filter(category=2).order_by('created_date').reverse
        log_files =  LogFile.objects.all()
        log_destusers = LogDestUser.objects.all()
        logsfirst =  OperationLog.objects.first()
        print('ろぐですーーーーーーー',logs)
        print('ろぐですーーーーーーー',logsfirst)

        context['logs'] = logs
        context['logsfirst'] = logsfirst
        context['log_files'] = log_files
        context['log_destusers'] = log_destusers
        
        return context
