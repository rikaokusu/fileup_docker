from django import template
from accounts.models import User
from draganddrop.models import UploadManage,Group,Downloadtable

register = template.Library()

@register.filter
def get_created_user_name(value):
    current_user = User.objects.filter(pk=value).first()

    if current_user:
        if current_user.first_name and current_user.last_name:
            user_name = current_user.last_name + current_user.first_name
        elif current_user.last_name:
            user_name = current_user.last_name
        elif current_user.first_name:
            user_name = current_user.first_name
        else:
            user_name = current_user.email
    return user_name