from django import template
from accounts.models import User
from draganddrop.models import UploadManage,Group,Downloadtable

register = template.Library()

@register.filter
def get_operation_user_name(value):

    current_user = User.objects.filter(pk=value).first()

    return current_user.display_name