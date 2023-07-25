"""
URL configuration for Recruitments project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from forms import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('new_form/', views.new_form, name='new_form'),
    path('new_form/<int:form_id>/', views.new_form, name='new_form'),
    # path('new_form_submit/', views.form_submit, name='new_form_submit'),
    path('form/<int:form_id>', views.form_view, name='form_view'),
    path('all_forms/', views.all_forms, name='all_forms'),
    path('create_form/', views.create_form, name='create_form'),
    path('form_details/<int:form_id>/', views.form_detail, name='form_details'),
    path('edit_form_fields/<int:form_id>/', views.edit_form_fields, name='edit_form_fields'),
    path('', views.home, name='home'),
]
