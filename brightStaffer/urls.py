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
from django.conf.urls import url,include
from brightStafferapp import views,resetpassword
from django.contrib import admin
from django.contrib.auth import views as auth_views
from brightStafferapp import views



urlpatterns =[
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('brightStafferapp.urls')),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.user_logout),
    url(r'^dashboard/$', views.dashboard),
    url(r'^account/$', views.register),
    url(r'^forgot/$', resetpassword.ResetPasswordRequestView.as_view()),
    url(r'^account/reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', resetpassword.PasswordResetConfirmView.as_view(),name='reset_password_confirm'),

]

