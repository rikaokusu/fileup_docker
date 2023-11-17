from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import OTPUploadManage, OTPDownloadtable
register = template.Library()


@register.filter
def otp_get_download_status(model_obj, value):
    otpdownloadtable = OTPDownloadtable.objects.filter(dest_user=value, otp_upload_manage=model_obj).first()

    if otpdownloadtable:
        return otpdownloadtable.is_downloaded

    else:
        return None
