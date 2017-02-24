from django.contrib import admin
from brightStafferapp.models import Projects, Concept, Talent, Company, TalentCompany


class CompanyInline(admin.TabularInline):
    model = Talent.company.through


class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recruiter', 'project_name', 'company_name', 'location', 'create_date')
    list_filter = ('recruiter', 'project_name', 'company_name', 'create_date')
    list_per_page = 2000


class ConceptsAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'concept')
    list_filter = ('id', 'project')
    list_per_page = 2000


class TalentAdmin(admin.ModelAdmin):
    list_display = ('id', 'recruiter', 'project', 'current_location', 'create_date', 'talent_name')
    list_filter = ('id', 'talent_name')
    filter_horizontal = ('company', )
    list_per_page = 2000
    # raw_id_fields = ('company',)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name')
    list_filter = ('id', 'company_name')
    list_per_page = 2000

admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Concept, ConceptsAdmin)
admin.site.register(Talent, TalentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(TalentCompany)


