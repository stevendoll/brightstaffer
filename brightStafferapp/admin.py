from django.contrib import admin
from brightStafferapp.models import Projects, Concept, Talent, Company, TalentCompany, Education, TalentEducation, \
    TalentProject, TalentConcept, ProjectConcept


class TalentCompanyInline(admin.TabularInline):
    model = TalentCompany
    extra = 1


class TalentConceptInline(admin.TabularInline):
    model = TalentConcept
    extra = 1


class ProjectConceptInline(admin.TabularInline):
    model = ProjectConcept
    extra = 1


class TalentEducationInline(admin.TabularInline):
    model = TalentEducation
    extra = 1


class TalentProjectInline(admin.TabularInline):
    model = TalentProject
    extra = 1


class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recruiter', 'project_name', 'company_name', 'location', 'create_date')
    list_filter = ('recruiter', 'project_name', 'company_name', 'create_date')
    list_per_page = 2000
    inlines = (ProjectConceptInline, )


class ConceptsAdmin(admin.ModelAdmin):
    list_display = ('id', 'concept')
    list_filter = ('id', )
    list_per_page = 2000


class TalentAdmin(admin.ModelAdmin):
    list_display = ('id', 'talent_name', 'recruiter', 'current_location', 'create_date', 'email_id')
    list_filter = ('id', 'talent_name')
    list_display_links = ('id', 'talent_name', 'recruiter')
    # filter_horizontal = ('company', )
    list_per_page = 2000
    inlines = (TalentProjectInline, TalentEducationInline, TalentCompanyInline, TalentConceptInline, )
    # raw_id_fields = ('company',)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name')
    list_filter = ('id', 'company_name')
    list_per_page = 2000


class ProjectConceptAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'concept', 'date_created')
    list_filter = ('project__project_name',)

admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Concept, ConceptsAdmin)
admin.site.register(Talent, TalentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(TalentCompany)
admin.site.register(Education)
admin.site.register(TalentEducation)
admin.site.register(TalentProject)
admin.site.register(ProjectConcept, ProjectConceptAdmin)


