from django.contrib import admin
from .models import User, Company, Service

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_login', 'is_superuser', 'is_active', 'is_staff', 'is_activate', 'display_name', 'email', 'last_name', 'middle_name', 'first_name', 'description', 'created_date')
    list_display_links = ('id',)

    # def _group(self, row):
    #     return ','.join([x.name for x in row.group.all()])

    # def _service(self, row):
    #     return ','.join([x.name for x in row.service.all()])


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'pic_company_name', 'pic_dept_name', 'pic_full_name', 'pic_post_code', 'pic_address', 'pic_tel_number', )
    list_display_links = ('pic_company_name', 'pic_dept_name', 'pic_full_name', 'pic_post_code', 'pic_address', 'pic_tel_number', )

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'initial', 'icon', 'number')
    list_display_links = ('name', 'description')


admin.site.register(User, UserAdmin,)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Service, ServiceAdmin)
