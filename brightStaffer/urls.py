"""brightStaffer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Homeo
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from brightStafferapp import views, resetpassword, talent


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_account/', views.UserData.as_view(), name='user_signup'),
    url(r'^user_login/', views.UserLogin.as_view(), name='user_login'),
    url(r'^forget/$', resetpassword.ForgetPassword.forget, name='forget_password'),
    url(r'^account/reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        resetpassword.ResetPassword.passwordresetconfirmView, name='reset_password_confirm'),
    url(r'^resetapi/$', resetpassword.ResetPassword.resetpasswordApi, name='reset_password_api'),

    url(r'^job_posting/$', views.JobPosting.as_view(), name='JobPosting'),
    url(r'^alchemy_analysis/$', views.AlchemyAPI.as_view(), name='JobPosting'),
    url(r'^update_concept/$', views.UpdateConcepts.as_view(), name='Update Concept'),
    url(r'^backbuttoninfo/$', views.BackButtonInfo.as_view(), name='Back Button Info'),
    url(r'^publish_jobPost/$', views.Publish.as_view(), name='Publish Project'),
    url(r'^project_list/$', views.ProjectList.as_view()),
    url(r'^top_project_list/$', views.TopProjectList.as_view()),
    url(r'^upload/$', views.FileUploadView.as_view(), name="file-upload"),
    url(r'^talent_list/$', talent.TalentList.as_view()),
    url(r'^insert_talent/$', talent.InsertTalent.as_view()),
    url(r'', views.home),

]
