"""brightStaffer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('brightStafferapp.urls')),
    url(r'^login/$', views.login, {'template_name': 'Login.html'}),
    url(r'^sign_up/$', views.login, {'template_name': 'Account.html'}),
    url(r'^forgot_password/$', views.login, {'template_name': 'Forgot_Password.html'}),
    url(r'^dashboard/$', views.login, {'template_name': 'Dashboard.html'}),

]
