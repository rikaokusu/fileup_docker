from django import template
from accounts.models import User
from draganddrop.models import UploadManage,Group,Downloadtable

register = template.Library()

@register.filter
def get_user_email(value):

    current_user = User.objects.filter(pk=value).first()

    return current_user.email