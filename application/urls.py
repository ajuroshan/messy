from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('apply/',apply,name='apply'),
    path('profile/',home,name='profile'),
    ]
