from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage,Downloadtable
register = template.Library()

@register.filter
def get_download_status(model_obj, value):
    downloadtable = Downloadtable.objects.filter(dest_user=value, upload_manage=model_obj).first()
    
    if downloadtable:
        return downloadtable.is_downloaded

    else:
        return None
