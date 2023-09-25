from django.urls import path, include
from . import views

app_name = 'contracts'


urlpatterns = [

    path('contract/', views.ContractIndexView.as_view(), name='contract'),
    path('trial_contract_reg/', views.TrialContractRegAjaxView.as_view(), name='trial_contract_reg'),

]
