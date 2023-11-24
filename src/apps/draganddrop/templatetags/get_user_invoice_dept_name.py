from django import template
from accounts.models import User, Company
from draganddrop.models import UploadManage,Group,Downloadtable

register = template.Library()

@register.filter
def get_user_invoice_dept_name(value):

    current_user = User.objects.filter(pk=value).first()

    return current_user.company.invoice_dept_name