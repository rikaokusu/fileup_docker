from django import template
from accounts.models import User,Company
from draganddrop.models import UploadManage,Group,Downloadtable

register = template.Library()

@register.filter
def get_created_user_company(value):
    user = User.objects.filter(pk=value).first()

    if user.company.pic_company_name and not user.company.pic_legal_personality == 99:
        if user.company.pic_legal_person_posi == '1':
            if user.company.pic_dept_name:
                company_name = user.company.get_pic_legal_personality_display() + user.company.pic_company_name + '　' + user.company.pic_dept_name
            else:
                company_name = user.company.get_pic_legal_personality_display() + user.company.pic_company_name
        else:
            if user.company.pic_dept_name:
                company_name = user.company.pic_company_name + user.company.get_pic_legal_personality_display() + '　' + user.company.pic_dept_name
            else:
                company_name = user.company.pic_company_name + user.company.get_pic_legal_personality_display()
    elif user.company.pic_company_name and user.company.pic_legal_personality == 99:
        if user.company.pic_dept_name:
            company_name = user.company.pic_company_name + '　' + user.company.pic_dept_name
        else:
            company_name = user.company.pic_company_name
    elif user.company.pic_company_name:
        company_name = user.company.pic_company_name
    else:
        company_name = user.email
    return company_name