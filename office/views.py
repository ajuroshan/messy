from django.shortcuts import render
import csv
import logging
import smtplib
from datetime import datetime as dt
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader
from django.utils.html import strip_tags

from django.http import HttpResponse
from django.shortcuts import render, redirect

from mess.models import MessAttendance
from mess.views import send_html_email
from .models import *
from mess.forms import *
from application.models import Application
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Subquery, OuterRef
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.template import loader
from django.conf import settings

from mess.views import calculate_total_messcut_days


# Create your views here.


@staff_member_required
def attendance_details_admin(request):
    today = date.today()
    if request.method == "POST":
        try:
            today = dt.strptime(request.POST.get("date"), "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Invalid date format")
    context = {}

    hostel = (
        Application.objects.filter(applicant=request.user, accepted=True).first().hostel
    )
    attendance_today = MessAttendance.objects.filter(
        timestamp__day=today.day,
        timestamp__month=today.month,
        timestamp__year=today.year,
        hostel=hostel,
    )
    breakfast_attendance = attendance_today.filter(meal="breakfast")
    lunch_attendance = attendance_today.filter(meal="lunch")
    dinner_attendance = attendance_today.filter(meal="dinner")

    context["today"] = today
    context["breakfast_attendance"] = breakfast_attendance
    context["lunch_attendance"] = lunch_attendance
    context["dinner_attendance"] = dinner_attendance
    return render(request, "admin/attendance_details.html", context)


@staff_member_required
def mess_bill_admin(request):
    try:
        hostel = (
            Application.objects.filter(applicant=request.user, accepted=True)
            .first()
            .hostel
        )
        messsettings = Messsettings.objects.filter(hostel=hostel).first()
    except Messsettings.DoesNotExist:
        # Handle case where no Messsettings instance exists
        return HttpResponse("Error: Messsettings instance not found")

    if request.method == "POST":
        form = MesssettingsForm(request.POST, request.FILES, instance=messsettings)
        if form.is_valid():
            form.save()
            calculate_mess_bill(hostel)
            return redirect("view_mess_bill_admin")
        else:
            print(form.errors)
            return HttpResponse("Error: Invalid form data")

    else:
        form = MesssettingsForm(instance=messsettings)

    return render(request, "admin/mess_bill_admin.html", {"form": form})


@staff_member_required
def view_mess_bill_admin(request):
    try:
        hostel = (
            Application.objects.filter(applicant=request.user, accepted=True)
            .first()
            .hostel
        )
        messsettings = Messsettings.objects.filter(hostel=hostel).first()
    except Messsettings.DoesNotExist:
        # Handle case where no Messsettings instance exists
        return HttpResponse("Error: Messsettings instance not found")

    if request.method == "POST":
        publish = (
            request.POST.get("publish") == "true"
        )  # Check if the publish button was clicked
        if publish:
            messsettings.publish_mess_bill = True
        else:
            messsettings.publish_mess_bill = False
        messsettings.save()

    subquery = (
        Application.objects.filter(mess_bill=OuterRef("pk"), hostel=hostel)
        .order_by("mess_no_number")
        .values("mess_no_number")[:1]
    )
    mess_bills = (
        MessBill.objects.filter(
            month__month=messsettings.month_for_bill_calculation.month, hostel=hostel
        )
        .annotate(mess_no_number=Subquery(subquery))
        .order_by("mess_no_number")
    )

    return render(
        request,
        "admin/mess_bills_table.html",
        {"mess_bills": mess_bills, "messsettings": messsettings},
    )


@staff_member_required
def download_mess_bill_admin(request):
    try:
        hostel = (
            Application.objects.filter(applicant=request.user, accepted=True)
            .first()
            .hostel
        )
        messsettings = Messsettings.objects.filter(hostel=hostel).first()
    except Messsettings.DoesNotExist:
        # Handle case where no Messsettings instance exists
        return HttpResponse("Error: Messsettings instance not found")

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f"attachment; filename={messsettings.hostel}-{messsettings.month_for_bill_calculation.strftime('%B %Y')} Messbill.csv"
    )

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row to the CSV file
    writer.writerow(
        [
            "Mess No",
            "Name",
            "Department",
            "Semester",
            "Outmess",
            "Official Outmess",
            "Claim",
            "Total Days",
            "Effective Days",
            "Amount Per Day",
            "Establishment Charges",
            "Feast Charges",
            "Other Charges",
            "Mess Cuts",
            "Effective Mess Cuts",
            "Total Amount",
            "Paid",
            "Date Paid",
        ]
    )

    mess_bills = MessBill.objects.filter(
        month__month=messsettings.month_for_bill_calculation.month, hostel=hostel
    ).order_by("application__mess_no_number")

    # Write data rows to the CSV file
    for bill in mess_bills:
        application = bill.application.last()  # Get the last related application
        if application:
            writer.writerow(
                [
                    application.mess_no,  # Mess No
                    f"{str(application.applicant.first_name).title()} {str(application.applicant.last_name).title()} "
                    if application.applicant.first_name
                    and application.applicant.last_name
                    else application.applicant.first_name,
                    # Applicant username
                    str(application.department).upper()
                    if application.department
                    else application.department,  # Department
                    application.semester,  # Semester
                    "Yes" if application.outmess else "No",
                    "Yes" if application.official_outmess else "No",
                    "Yes" if application.claim else "No",
                    bill.total_days,  # Total Days
                    bill.effective_days,  # Effective Days
                    bill.amount_per_day,  # Amount Per Day
                    bill.establishment_charges,  # Establishment Charges
                    bill.feast_charges,  # Feast Charges
                    bill.other_charges,  # Other Charges
                    bill.mess_cuts,  # Mess Cuts
                    bill.effective_mess_cuts,
                    bill.amount,  # Amount
                    "Yes" if bill.paid else "No",  # Paid
                    bill.date_paid.strftime("%Y-%m-%d")
                    if bill.date_paid
                    else "N/A",  # Date Paid
                ]
            )
        else:
            writer.writerow(
                ["N/A"] * 13
            )  # Handle cases where the application does not exist

    return response


@staff_member_required
def messcut_details_admin(request):
    today = date.today()
    hostel = (
        Application.objects.filter(applicant=request.user, accepted=True).first().hostel
    )
    if request.method == "POST":
        try:
            today = dt.strptime(request.POST.get("date"), "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Invalid date format")

    context = {}
    messcuts = Messcut.objects.filter(start_date__month=today.month, hostel=hostel)
    messcuts_today = Messcut.objects.filter(
        start_date__lte=today, end_date__gte=today, hostel=hostel
    )

    # Get all applications that have a mess cut today
    today_messcut_applications = Application.objects.filter(
        messcuts__start_date__lte=today,
        messcuts__end_date__gte=today,
        messcuts__hostel=hostel,
    ).distinct()

    # Prepare a list of tuples (application, messcut) for applications with today's mess cut
    applications_with_messcuts_today = []
    for application in today_messcut_applications:
        # Filter the mess cuts for today within this application
        for messcut in application.messcuts.filter(
            start_date__lte=today, end_date__gte=today
        ):
            applications_with_messcuts_today.append((application, messcut))

    total_students = Application.objects.filter(accepted=True, hostel=hostel).count()
    estimated_food = total_students - today_messcut_applications.count()
    application_count = today_messcut_applications.count()

    context["messcuts"] = messcuts
    context["messcuts_today"] = messcuts_today
    context["total_students"] = total_students
    context["estimated_food"] = estimated_food
    context["applications_with_messcuts_today"] = applications_with_messcuts_today
    context["application_count"] = application_count
    context["today"] = today
    print(context)

    return render(request, "admin/messcut_details.html", context)


@staff_member_required
def attendance_cut_details_admin(request):
    today = date.today()
    hostel = (
        Application.objects.filter(applicant=request.user, accepted=True).first().hostel
    )

    if request.method == "POST":
        try:
            today = dt.strptime(request.POST.get("date"), "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Invalid date format")

    # Get all accepted applications
    applications = Application.objects.filter(accepted=True, hostel=hostel)

    # Get today's attendance records and extract student IDs
    attendance_today = MessAttendance.objects.filter(
        timestamp__year=today.year,
        timestamp__month=today.month,
        timestamp__day=today.day,
        hostel=hostel,
    )

    # Extract student IDs who attended each meal
    breakfast_attended_students = attendance_today.filter(meal="breakfast").values_list(
        "student", flat=True
    )
    lunch_attended_students = attendance_today.filter(meal="lunch").values_list(
        "student", flat=True
    )
    dinner_attended_students = attendance_today.filter(meal="dinner").values_list(
        "student", flat=True
    )

    # Get all mess cuts valid today
    messcuts_today = Messcut.objects.filter(
        start_date__lte=today, end_date__gte=today, hostel=hostel
    )

    # Get all applications with mess cuts valid today
    applications_with_messcut = Application.objects.filter(
        messcuts__start_date__lte=today,
        messcuts__end_date__gte=today,
        hostel=hostel,
    ).distinct()

    # Exclude applications with a mess cut today
    valid_applications = applications.exclude(
        applicant__in=applications_with_messcut.values_list("applicant", flat=True)
    )

    # Calculate who didn't attend each meal
    breakfast_not_attended_details = valid_applications.exclude(
        applicant__in=breakfast_attended_students
    )
    lunch_not_attended_details = valid_applications.exclude(
        applicant__in=lunch_attended_students
    )
    dinner_not_attended_details = valid_applications.exclude(
        applicant__in=dinner_attended_students
    )

    # Render the results to a template
    context = {
        "today": today,
        "breakfast_not_attended": breakfast_not_attended_details,
        "lunch_not_attended": lunch_not_attended_details,
        "dinner_not_attended": dinner_not_attended_details,
    }
    return render(request, "admin/attendance_cut_details.html", context)


def calculate_mess_bill(hostel):
    messsettings = Messsettings.objects.filter(hostel=hostel).first()
    if not messsettings:
        raise ValueError("Messsettings instance is required to calculate mess bills.")

    # Constants
    BILL_DATE = messsettings.month_for_bill_calculation
    AMOUNT_PER_DAY = messsettings.amount_per_day
    ESTABLISHMENT_CHARGES = messsettings.establishment_charges
    TOTAL_DAYS = messsettings.total_days
    OTHER_CHARGES = messsettings.other_charges
    FEAST_CHARGES = messsettings.feast_charges
    MESS_CLOSED_DATES = [date.date for date in messsettings.mess_closed_dates.all()]

    mess_bills = MessBill.objects.filter(month__month=BILL_DATE.month, hostel=hostel)
    if mess_bills.exists():
        mess_bills.delete()

    # Iterate through accepted applications
    for application in Application.objects.filter(
        accepted=True, hostel=hostel
    ):
        # Calculate total messcut days for the given month
        messcuts = application.messcuts.filter(start_date__month=BILL_DATE.month)

        total_messcut_days = calculate_total_messcut_days(messcuts, hostel)
        effective_messcut_days = total_messcut_days

        for date in MESS_CLOSED_DATES:
            for messcut in messcuts:
                if date in messcut.get_date_range():
                    effective_messcut_days -= 1

        effective_messcut_days = max(effective_messcut_days, 0)

        effective_days = TOTAL_DAYS - effective_messcut_days
        total_amount = (AMOUNT_PER_DAY * effective_days) + (
            ESTABLISHMENT_CHARGES + OTHER_CHARGES + FEAST_CHARGES
        )

        # Create the mess bill
        mess_bill = application.mess_bill.get_or_create(
            amount=total_amount,
            month=messsettings.month_for_bill_calculation,
            paid=False,
            effective_days=effective_days,
            amount_per_day=AMOUNT_PER_DAY,
            establishment_charges=ESTABLISHMENT_CHARGES,
            other_charges=OTHER_CHARGES,
            feast_charges=FEAST_CHARGES,
            total_days=TOTAL_DAYS,
            mess_cuts=total_messcut_days,
            effective_mess_cuts=effective_messcut_days,
            hostel=hostel,
        )
        application.save()


def send_mess_bill_mail_admin(request):
    try:
        # Assume there is only one Messsettings instance
        hostel = (
            Application.objects.filter(applicant=request.user, accepted=True)
            .first()
            .hostel
        )
        messsettings = Messsettings.objects.filter(hostel=hostel).first()
    except Messsettings.DoesNotExist:
        # Handle case where no Messsettings instance exists
        return HttpResponse("Error: Messsettings instance not found")

    mess_bills = MessBill.objects.filter(
        month__month=messsettings.month_for_bill_calculation.month
    ).order_by("application__mess_no")

    failed_emails = []

    for bill in mess_bills:
        try:
            application = bill.application.last()
            if application:
                context = {
                    "subject": f"Monthly Mess Bill for {messsettings.month_for_bill_calculation.strftime('%B %Y')}",
                    "message": f"Hello {application.applicant.first_name} {application.applicant.last_name}! The monthly mess bill for {messsettings.month_for_bill_calculation.strftime('%B %Y')} is now available. Please click the link below to view your bill.",
                    "total_amount": bill.amount,
                    "action_url": "https://youtube.com",
                }
                if not send_html_email(
                    context["subject"], application.applicant.email, context
                ):
                    failed_emails.append(application.applicant.email)
        except Exception as e:
            logger.error(
                f"Error processing bill for application {bill.application.id}: {e}"
            )
            failed_emails.append(application.applicant.email)

    if failed_emails:
        return HttpResponse(
            f"Email sent with some failures. Failed emails: {', '.join(failed_emails)}"
        )

    return HttpResponse("Email sent successfully")


@staff_member_required()
def individual_attendance(request):
    if request.method == "POST":
        context = {}
        mess_no = request.POST.get("mess_no")
        hostel = (
            Application.objects.filter(applicant=request.user, accepted=True)
            .first()
            .hostel
        )
        mess_no = f"{hostel.code}-{mess_no}"
        date_of_attendance = request.POST.get("date_of_attendance")
        year_of_attendance = date_of_attendance.split("-")[0]
        month_of_attendance = date_of_attendance.split("-")[1]
        application = Application.objects.filter(mess_no__exact=mess_no)
        if not application:
            context["message"] = "Mess number not found!"
            return render(request, "admin/individual_attendance.html", context)
        total_attendance = MessAttendance.objects.filter(
            student=application.first(),
            timestamp__month=month_of_attendance,
            timestamp__year=year_of_attendance,
        )
        breakfast_attendance = total_attendance.filter(meal="breakfast")
        lunch_attendance = total_attendance.filter(meal="lunch")
        dinner_attendance = total_attendance.filter(meal="dinner")

        context["breakfast_attendance"] = breakfast_attendance
        context["lunch_attendance"] = lunch_attendance
        context["dinner_attendance"] = dinner_attendance
        context["name_of_student"] = (
            application.first().first_name + " " + application.first().last_name
        )
        return render(request, "admin/individual_attendance.html", context)
    return render(request, "admin/individual_attendance.html")



@staff_member_required
def individual_messcut(request):
    context = {}

    if request.method == "POST":
        mess_no = request.POST.get("mess_no")
        date_of_attendance = request.POST.get("date_of_attendance")
        hostel = (
            Application.objects.filter(applicant=request.user, accepted=True)
            .first()
            .hostel
        )
        mess_no = f"{hostel.code}-{mess_no}"

        if date_of_attendance:
            year_of_attendance = int(date_of_attendance.split("-")[0])
            month_of_attendance = int(date_of_attendance.split("-")[1])

            # Get the hostel of the logged-in user's accepted application
            application = Application.objects.filter(mess_no__exact=mess_no, hostel=hostel).first()
            if application and application.hostel:

                # Filter messcuts for that year+month
                messcuts = application.messcuts.filter(
                    start_date__year=year_of_attendance,
                    start_date__month=month_of_attendance,
                    hostel=application.hostel,
                )

                total_messcut_days = calculate_total_messcut_days(messcuts, hostel)

                # Add everything to context
                context.update({
                    "mess_no": mess_no,
                    "messcuts": messcuts,
                    "total_messcut_days": total_messcut_days,
                    "name_of_student": f"{application.applicant.first_name} {application.applicant.last_name}",
                })

    return render(request, "admin/individual_messcut.html", context)
