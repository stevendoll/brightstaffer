from django.contrib import admin
from brightStafferapp.models import Projects,Concepts




class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recuriter','project_name','company_name','location','create_date','is_published')
    list_filter = ('recuriter','project_name','company_name','create_date')
    list_per_page = 2000


class ConceptsAdmin(admin.ModelAdmin):
    list_display = ('id', 'project','concepts')
    list_filter = ('id','project')
    list_per_page = 2000

admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Concepts, ConceptsAdmin)


