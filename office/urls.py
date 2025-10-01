from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("mess_bill_admin/", mess_bill_admin, name="mess_bill_admin"),
    path("view_mess_bill_admin/", view_mess_bill_admin, name="view_mess_bill_admin"),
    path(
        "download_mess_bill_admin/",
        download_mess_bill_admin,
        name="download_mess_bill_admin",
    ),
    path(
        "send_mess_bill_mail_admin/",
        send_mess_bill_mail_admin,
        name="send_mess_bill_mail_admin",
    ),
    path("messcut_details_admin/", messcut_details_admin, name="messcut_details_admin"),
    path(
        "attendance_details_admin/",
        attendance_details_admin,
        name="attendance_details_admin",
    ),
    path(
        "attendance_cut_details_admin/",
        attendance_cut_details_admin,
        name="attendance_cut_details_admin",
    ),
    path("individual_attendance/", individual_attendance, name="individual_attendance"),
    path("individual_messcut/", individual_messcut, name="individual_messcut"),
    path("total_messcuts/", total_messcuts, name="total_messcuts"),
]
