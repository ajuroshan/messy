from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from application.models import Application
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Subquery, OuterRef

from .forms import MesssettingsForm


# Create your views here.
@login_required
def apply_for_messcut(request):
	application = Application.objects.filter(applicant=request.user).first()
	messcuts = application.messcuts.filter(start_date__month=datetime.today().month)
	total_messcut_days = sum((messcut.end_date - messcut.start_date).days + 1 for messcut in messcuts)
	if request.method == 'POST':
		form = MesscutForm(request.POST, request=request)
		if form.is_valid():
			messcut = form.save(commit=False)
			# Find the accepted application for the current user
			applicant = Application.objects.filter(applicant=request.user, accepted=True).first()

			if applicant:
				messcut.save()  # Save the Messcut instance first
				applicant.messcuts.add(messcut)  # Add the Messcut to the applicant's messcuts
				applicant.save()  # Save the Application instance to update the M2M relationship

				return redirect('home')
			else:
				# Handle the case where no accepted application exists
				return HttpResponse("You need to apply for a mess first")
	else:
		form = MesscutForm()

	return render(request, 'mess/apply.html',
	              {'form': form, 'total_messcut_days': total_messcut_days, 'messcuts': messcuts})


def group_required(group_name):
	def in_group(user):
		return user.is_authenticated and user.groups.filter(name=group_name).exists()

	return user_passes_test(in_group, login_url='home', redirect_field_name=None)


@group_required('mess_assistants')
def scan_qr(request):
	current_time = timezone.localtime().time()

	# Define meal times (local time)
	breakfast_time = (time(8, 0), time(10, 0))  # Breakfast is served from 8 AM to 10 AM
	lunch_time = (time(12, 10), time(14, 45))  # Lunch is served from 12:10 PM to 12:45 PM
	dinner_time = (time(20, 0), time(21, 0))  # Dinner is served from 8 PM to 9 PM

	# Set meal based on current local time
	if (breakfast_time[0] <= current_time < breakfast_time[1]) or (lunch_time[0] <= current_time < lunch_time[1]) or (
			dinner_time[0] <= current_time < dinner_time[1]):
		return render(request, 'mess/scan_qr.html', {'mealtime': True})
	else:
		return render(request, 'mess/scan_qr.html', {'mealtime': True})


@group_required('mess_assistants')
@login_required
@csrf_exempt
def mark_attendance(request):
	if request.method == 'POST':
		print(request.POST)
		qr_code_data = request.POST.get('qr_code_data')
		mess_no = request.POST.get('mess_no')
		confirm = request.POST.get('confirm') == 'true'
		current_time = timezone.localtime().time()

		# Define meal times (local time)
		breakfast_time = (time(8, 0), time(10, 0))
		lunch_time = (time(12, 10), time(14, 45))
		dinner_time = (time(16, 0), time(21, 0))

		MEAL_CHOICES = [
			('breakfast', 'Breakfast'),
			('lunch', 'Lunch'),
			('dinner', 'Dinner'),
		]

		if breakfast_time[0] <= current_time < breakfast_time[1]:
			meal = MEAL_CHOICES[0][0]
		elif lunch_time[0] <= current_time < lunch_time[1]:
			meal = MEAL_CHOICES[1][0]
		elif dinner_time[0] <= current_time < dinner_time[1]:
			meal = MEAL_CHOICES[2][0]
		else:
			meal = "No meal time"

		meal_attendance = MessAttendance.objects.filter(
			meal=meal,
			timestamp__day=datetime.today().day,
			timestamp__month=datetime.today().month,
			timestamp__year=datetime.today().year
		).count()

		if mess_no and not qr_code_data:
			qr_code_data = mess_no

		try:
			qr_code_data = int(qr_code_data)
		except ValueError:
			return JsonResponse({
				"status"     : "error",
				"message"    : "Invalid QR Code",
				"app_details": {}
			}, status=400)

		application = Application.objects.filter(mess_no=qr_code_data, accepted=True).first()
		if application:
			app_details = {
				"full_name": f"{application.applicant.first_name + ' ' + application.applicant.last_name}",
				"dept"     : str(application.department).upper(),
				"mess_no"  : application.mess_no,
			}
			messcuts = application.messcuts.filter(start_date__month=datetime.today().month)
			for messcut in messcuts:
				if messcut.start_date <= date.today() <= messcut.end_date:
					return JsonResponse({
						"status"         : "error",
						"message"        : "You cannot mark attendance during messcut period.",
						"app_details"    : app_details,
						"messcut"        : f"Messcut from {messcut.start_date} to {messcut.end_date}",
						"meal_attendance": meal_attendance
					}, status=400)

			if confirm:
				try:
					attendance = MessAttendance.objects.create(
						student=application,
						meal=meal,
						timestamp=timezone.now()
					)
					meal_attendance = MessAttendance.objects.filter(
						meal=meal,
						timestamp__day=datetime.today().day,
						timestamp__month=datetime.today().month,
						timestamp__year=datetime.today().year
					).count()
					return JsonResponse({
						"status"         : "success",
						"message"        : f"Attendance for {app_details['mess_no']}  marked successfully",
						"app_details"    : app_details,
						"meal_attendance": meal_attendance
					}, status=200)
				except Exception as e:
					return JsonResponse({
						"status"         : "error",
						"message"        : f"Attendance already marked for {app_details['mess_no']}",
						"app_details"    : app_details,
						"meal_attendance": meal_attendance
					}, status=400)
			else:
				return JsonResponse({
					"status"         : "error",
					"message"        : "Please confirm to mark attendance.",
					"app_details"    : app_details,
					"meal_attendance": meal_attendance
				}, status=400)
		else:
			return JsonResponse({
				"status"         : "error",
				"message"        : "No application found",
				"meal_attendance": meal_attendance
			}, status=400)
	else:
		return JsonResponse({
			"status"     : "error",
			"message"    : "GET request not allowed",
			"app_details": {},
		}, status=404)


@login_required
def dashboard(request):
	application = Application.objects.filter(applicant=request.user).first()
	return render(request, 'mess/dashboard.html', {'application': application})


@login_required
def view_mess_bill(request):
	try:
		# Assume there is only one Messsettings instance
		messsettings = Messsettings.objects.first()
	except Messsettings.DoesNotExist:
		# Handle case where no Messsettings instance exists
		return redirect('some_error_page')
	application = Application.objects.filter(applicant=request.user).first()
	mess_bill = application.mess_bill.filter(month__month=messsettings.month_for_bill_calculation.month).last()
	details = Messsettings.objects.first()

	return render(request, 'mess/view_mess_bill.html',
	              {'mess_bill': mess_bill, "application": application, "details": details})


def pay_mess_bill(request):
	application = Application.objects.filter(applicant=request.user).first()
	mess_bill = application.mess_bill.filter(month__month=date.today().month).last()

	if request.method == 'POST':
		form = PayMessBillForm(request.POST, request.FILES, instance=mess_bill)
		if form.is_valid():
			mess_bill = form.save(commit=False)
			mess_bill.paid = True
			mess_bill.date_paid = date.today()
			mess_bill.save()

			return redirect('home')
	else:
		form = PayMessBillForm(instance=mess_bill)

	return render(request, 'mess/pay_mess_bill.html',
	              {'form': form, 'mess_bill': mess_bill, "application": application})


@login_required
def weekly_menu(request):
	weekly_menu = Messmenu.objects.all().order_by('id')  # Get the full week's menu

	context = {
		'weekly_menu': weekly_menu,
	}
	return render(request, 'mess/menu.html', context)


@staff_member_required
def mess_bill_admin(request):
	try:
		# Assume there is only one Messsettings instance
		messsettings = Messsettings.objects.first()
	except Messsettings.DoesNotExist:
		# Handle case where no Messsettings instance exists
		return HttpResponse('Error: Messsettings instance not found')

	if request.method == 'POST':
		form = MesssettingsForm(request.POST, request.FILES, instance=messsettings)
		if form.is_valid():
			form.save()
			calculate_mess_bill()
			return redirect('view_mess_bill_admin')
		else:
			return HttpResponse('Error: Invalid form data')

	else:
		form = MesssettingsForm(instance=messsettings)

	return render(request, 'admin/mess_bill_admin.html', {'form': form})


def view_mess_bill_admin(request):
	try:
		# Assume there is only one Messsettings instance
		messsettings = Messsettings.objects.first()
	except Messsettings.DoesNotExist:
		# Handle case where no Messsettings instance exists
		return HttpResponse('Error: Messsettings instance not found')

	if request.method == 'POST':
		publish = request.POST.get('publish') == 'true'  # Check if the publish button was clicked
		if publish:
			messsettings.publish_mess_bill = True
		else:
			messsettings.publish_mess_bill = False
		messsettings.save()

	subquery = Application.objects.filter(mess_bill=OuterRef('pk')).order_by('mess_no').values('mess_no')[:1]
	mess_bills = MessBill.objects.filter(month__month=messsettings.month_for_bill_calculation.month).annotate(
		mess_no=Subquery(subquery)).order_by('mess_no')

	return render(request, 'admin/mess_bills_table.html',
	              {'mess_bills': mess_bills, 'messsettings': messsettings})


def calculate_mess_bill():
	# Fetch Messsettings only once
	messsettings = Messsettings.objects.first()
	if not messsettings:
		raise ValueError("Messsettings instance is required to calculate mess bills.")

	# Constants
	MONTH = messsettings.month_for_bill_calculation.month
	AMOUNT_PER_DAY = messsettings.amount_per_day
	ESTABLISHMENT_CHARGES = messsettings.establishment_charges
	TOTAL_DAYS = messsettings.total_days
	OTHER_CHARGES = messsettings.other_charges
	FEAST_CHARGES = messsettings.feast_charges

	mess_bills = MessBill.objects.filter(month__month=MONTH)
	if mess_bills.exists():
		mess_bills.delete()

	# Iterate through accepted applications
	for application in Application.objects.filter(accepted=True):
		# Calculate total messcut days for the given month
		messcuts = application.messcuts.filter(start_date__month=MONTH)
		total_messcut_days = sum((messcut.end_date - messcut.start_date).days + 1 for messcut in messcuts)

		# Calculate effective days and total amount
		effective_days = TOTAL_DAYS - total_messcut_days
		total_amount = (AMOUNT_PER_DAY * effective_days) + (ESTABLISHMENT_CHARGES + OTHER_CHARGES + FEAST_CHARGES)

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
			mess_cuts=total_messcut_days
		)
		# Save the application if needed (if changes made to application itself)
		application.save()

# TODO: Implement functionality for exporting bill data to CSV if required
