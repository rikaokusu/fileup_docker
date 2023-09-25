from django.contrib import admin
from contracts.models import Contract, Plan


class ContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'plan', 'status', 'contract_start_date', 'contract_end_date', 'pay_start_date', 'pay_end_date', 'minor_total', 'tax', 'total', 'is_autocheckout', 'is_invoice_need',)
    list_display_links = ('user', 'service', 'status', 'contract_start_date', 'contract_end_date', 'pay_start_date', 'pay_end_date',)


class PlanAdmin(admin.ModelAdmin):
    list_display = ('is_option', 'is_trial', 'service', 'category', 'payjp_plan_id', 'name', 'price', 'unit_price', 'user_num', 'description',)
    list_display_links =('payjp_plan_id', 'name', 'price', 'user_num', 'description',)


admin.site.register(Contract, ContractAdmin,)
admin.site.register(Plan, PlanAdmin,)
