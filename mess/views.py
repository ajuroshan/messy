import csv
import logging
import smtplib
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader
from django.utils.html import strip_tags

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
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.template import loader
from django.conf import settings
from datetime import datetime
from .forms import MesssettingsForm
from .tasks import send_html_email


logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def apply_for_messcut(request):
	messcut_closing_time = Messsettings.objects.first().messcut_closing_time
	can_mark_messcut = timezone.localtime().time() < messcut_closing_time
	application = Application.objects.filter(applicant=request.user).first()
	messcuts = application.messcuts.filter(start_date__month=datetime.today().month)
	prev_messcuts = application.messcuts.filter(start_date__month__lte=datetime.today().month,start_date__year__lte=datetime.today().year)
	future_messcuts = application.messcuts.exclude(start_date__month__lte=datetime.today().month,start_date__year__lte=datetime.today().year)
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
				messcuts = application.messcuts.filter(start_date__month=datetime.today().month)
				total_messcut_days = sum((messcut.end_date - messcut.start_date).days + 1 for messcut in messcuts)
				#send_html_email("Mess Cut Confirmation", request.user.email , {"subject":"Mess Cut Confirmation","user":request.user,"start_date": messcut.start_date,"end_date": messcut.end_date})
				send_html_email.delay("Mess Cut Confirmation", request.user.email , {"subject":"Mess Cut Confirmation",
				                                                                     "user_name": f"{request.user.first_name } {request.user.last_name}",
				                                                                     "start_date": messcut.start_date,
				                                                                     "end_date": messcut.end_date,
				                                                                     "total_messcut_days": total_messcut_days})
				return render(request, 'mess/apply.html',
				              {'form'   : form, 'total_messcut_days': total_messcut_days, 'messcuts': messcuts,"prev_messcuts":prev_messcuts,"future_messcuts":future_messcuts,
				               'message': 'Messcut applied successfully', 'can_mark_messcut': can_mark_messcut,'messcut_closing_time': messcut_closing_time})
			else:
				# Handle the case where no accepted application exists
				return HttpResponse("You need to apply for a mess first")
	else:
		form = MesscutForm()

	return render(request, 'mess/apply.html',
	              {'form': form, 'total_messcut_days': total_messcut_days, 'messcuts': messcuts,"prev_messcuts":prev_messcuts,"future_messcuts":future_messcuts,'can_mark_messcut': can_mark_messcut,'messcut_closing_time': messcut_closing_time})


def group_required(group_name):
	def in_group(user):
		return user.is_authenticated and user.groups.filter(name=group_name).exists()

	return user_passes_test(in_group, login_url='home', redirect_field_name=None)


@group_required('mess_assistants')
def scan_qr(request):
	current_time = timezone.localtime().time()

	# Fetch meal times from Messsettings
	try:
		mess_settings = Messsettings.objects.first()
	except Messsettings.DoesNotExist:
		# Handle case where no Messsettings instance exists
		return HttpResponse('Error: Messsettings instance not found')

	# Set mealtime to True if the current time falls within any meal period
	mealtime = (mess_settings.breakfast_start_time <= current_time < mess_settings.breakfast_end_time) or \
	           (mess_settings.lunch_start_time <= current_time < mess_settings.lunch_end_time) or \
	           (mess_settings.dinner_start_time <= current_time < mess_settings.dinner_end_time)

	return render(request, 'mess/scan_qr.html', {'mealtime': mealtime})


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

		# Fetch meal times from Messsettings
		mess_settings = Messsettings.objects.first()

		# Set meal based on current local time
		if mess_settings.breakfast_start_time <= current_time < mess_settings.breakfast_end_time:
			meal = 'breakfast'
		elif mess_settings.lunch_start_time <= current_time < mess_settings.lunch_end_time:
			meal = 'lunch'
		elif mess_settings.dinner_start_time <= current_time < mess_settings.dinner_end_time:
			meal = 'dinner'
		else:
			meal = None

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


@login_required
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



def attendance_details(request):
	current_datetime = datetime.now()
	context = {}
	total_attendance = MessAttendance.objects.filter(student=Application.objects.filter(applicant=request.user).first(),timestamp__month=date.today().month,timestamp__year=date.today().year)
	breakfast_attendance = total_attendance.filter(meal='breakfast')
	lunch_attendance = total_attendance.filter(meal='lunch')
	dinner_attendance = total_attendance.filter(meal='dinner')

	context['breakfast_attendance'] = breakfast_attendance
	context['lunch_attendance'] = lunch_attendance
	context['dinner_attendance'] = dinner_attendance
	context['current_datetime'] = current_datetime
	return render(request, 'mess/attendance_details.html',context)



def feedback(request):
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			feedback_form = form.save(commit=False)
			application = Application.objects.filter(applicant=request.user).first()
			feedback_form.student = application
			feedback_form.save()
			return redirect('home')
	else:
		form = FeedbackForm()

	return render(request, 'mess/feedback.html', {'form': form})



# def send_html_email(subject, to_email, context):
# 	try:
# 		# Load the template
# 		html_template = loader.get_template('email/email_template.html')
#
# 		# Render the template with context
# 		html_content = html_template.render(context)
#
# 		# Strip the HTML content to create a plain text version
# 		text_content = strip_tags(html_content)
#
# 		# Create the email
# 		email = EmailMultiAlternatives(
# 			subject=subject,
# 			body=text_content,  # Plain text content for email clients that don't support HTML
# 			from_email=settings.EMAIL_HOST_USER,
# 			to=[to_email]
# 		)
#
# 		# Attach the HTML content as an alternative
# 		email.attach_alternative(html_content, "text/html")
#
# 		# Send the email
# 		email.send()
# 	except Exception as e:
# 		logger.error(f'Failed to send email to {to_email}: {e}')
# 		return False
# 	return True
# TODO: Implement functionality for exporting bill data to CSV if required


from .tasks import add

def my_view(request):
	result = add.delay(4, 99)  # Task is called asynchronously
	return HttpResponse(f'Task ID: {result.task_id} and the result is {result.get()}')
