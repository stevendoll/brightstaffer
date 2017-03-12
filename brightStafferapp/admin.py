from django.contrib import admin
from brightStafferapp.models import Projects, Concept, Talent, Company, TalentCompany, Education, TalentEducation, \
    TalentProject, TalentConcept, ProjectConcept, FileUpload, PdfImages, TalentEmail, TalentContact, TalentStage, \
    Recruiter,TalentRecruiter


class TalentCompanyInline(admin.TabularInline):
    model = TalentCompany
    extra = 1
    ordering = ('-start_date', )


class TalentConceptInline(admin.TabularInline):
    model = TalentConcept
    extra = 0


class ProjectConceptInline(admin.TabularInline):
    model = ProjectConcept
    extra = 1


class TalentEducationInline(admin.TabularInline):
    model = TalentEducation
    extra = 1


class TalentProjectInline(admin.TabularInline):
    model = TalentProject
    extra = 1
    ordering = ('-date_added',)


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
    list_display = ('id', 'talent_name', 'recruiter', 'current_location', 'create_date')
    list_filter = ('id', 'talent_name')
    list_display_links = ('id', 'talent_name', 'recruiter')
    list_per_page = 2000
    inlines = (TalentProjectInline, TalentEducationInline, TalentCompanyInline, TalentConceptInline, )


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name')
    list_filter = ('id', 'company_name')
    list_per_page = 2000


class ProjectConceptAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'concept', 'date_created')
    list_filter = ('project__project_name',)


class TalentEmailAdmin(admin.ModelAdmin):
    list_display = ('talent', 'email')
    list_filter = ('talent',)


class TalentContactAdmin(admin.ModelAdmin):
    list_display = ('talent', 'contact')
    list_filter = ('talent',)


class TalentStageAdmin(admin.ModelAdmin):
    list_display = ('id','talent', 'project', 'stage', 'details', 'notes', 'date_created')
    list_filter = ('talent',)


class TalentRecruiterAdmin(admin.ModelAdmin):
    list_display = ('id','talent', 'recruiter', 'is_active')
    list_filter = ('talent',)

admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Concept, ConceptsAdmin)
admin.site.register(Talent, TalentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(TalentCompany)
admin.site.register(Education)
admin.site.register(TalentEducation)
admin.site.register(TalentProject)
admin.site.register(ProjectConcept, ProjectConceptAdmin)
admin.site.register(FileUpload)
admin.site.register(PdfImages)
admin.site.register(TalentEmail, TalentEmailAdmin)
admin.site.register(TalentContact, TalentContactAdmin)
admin.site.register(TalentStage, TalentStageAdmin)
admin.site.register(TalentRecruiter,TalentRecruiterAdmin)
admin.site.register(Recruiter)