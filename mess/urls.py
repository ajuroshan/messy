from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("apply_messcut/", apply_for_messcut, name="apply_for_messcut"),
    path("dashboard/", dashboard, name="dashboard"),
    path("mess_bill/", view_mess_bill, name="view_mess_bill"),
    path("pay_mess_bill/", pay_mess_bill, name="pay_mess_bill"),
    path("weekly_menu/", weekly_menu, name="weekly_menu"),
    path("scan_qr/", scan_qr, name="scan_qr"),
    path("mark_attendance/", mark_attendance, name="mark_attendance"),
    path("attendance_details/", attendance_details, name="attendance_details"),
    path("feedback/", feedback, name="feedback"),
    path("addd/", my_view, name="my_view"),
]
