from django.contrib import admin
from brightStafferapp.models import Account,Projects,Resume,Job_Posting,Candidate,Project_Activity


class AccountAdmin(admin.ModelAdmin):
    list_display = ('client_id','client_name','active','domain_name','account_manager')
    list_filter = ('client_id', "client_name")
    list_per_page = 2000

class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'recuriter', 'client', 'title', 'description','industry','functional','minexp','maxexp','minsalary','maxsalary','location','jtype','qualification')
    list_filter = ('project_id', "client")
    list_per_page = 2000

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('email','resume')
    list_filter = ('email',)
    list_per_page = 2000

class Job_PostingAdmin(admin.ModelAdmin):
    list_display = ('email','job_description')
    list_filter = ('email',)
    list_per_page = 2000

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('candidate_id','recuriter','client','email','name','location','agree','gender','exp','title','company','skills','sector','functional','minsalary','qualification','specialization','certification','institute','passing','jtype','pubdate')
    list_filter = ('candidate_id', "client")
    list_per_page = 2000

class Project_ActivityAdmin(admin.ModelAdmin):
    list_display = ('project_activity_id','project','recuriter','candidate','action_type','date','details','summary')
    list_filter = ('project_activity_id', "recuriter","candidate")
    list_per_page = 2000


admin.site.register(Account, AccountAdmin)
admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Resume, ResumeAdmin)
admin.site.register(Job_Posting, Job_PostingAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Project_Activity, Project_ActivityAdmin)
