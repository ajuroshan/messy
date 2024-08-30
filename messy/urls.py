"""
URL configuration for messy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static

from django.conf import settings

from mess.views import mess_bill_admin, view_mess_bill_admin, download_mess_bill_admin, send_mess_bill_mail_admin

urlpatterns = [
	path('admin/mess_bill_admin/', mess_bill_admin, name='mess_bill_admin'),
	path('admin/view_mess_bill_admin/', view_mess_bill_admin, name='view_mess_bill_admin'),
	path('admin/download_mess_bill_admin/', download_mess_bill_admin, name='download_mess_bill_admin'),
	path('admin/send_mess_bill_mail_admin/', send_mess_bill_mail_admin, name='send_mess_bill_mail_admin'),
	path('admin/messcut_details_admin/', send_mess_bill_mail_admin, name='send_mess_bill_mail_admin'),

	path('admin/', admin.site.urls,),
	path('', include('application.urls')),
	path('mess/', include('mess.urls')),
	path('accounts/', include('allauth.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
