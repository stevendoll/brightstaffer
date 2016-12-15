from django.contrib import admin
from brightStafferapp.models import Account,Projects,Resume,Job_Posting,Candidate,Project_Activity


class AccountAdmin(admin.ModelAdmin):
    list_display = ('client_id','client_name','active','domain_name','account_manager')
    list_filter = ('client_id', "client_name")
    list_per_page = 2000


admin.site.register(Account, AccountAdmin)