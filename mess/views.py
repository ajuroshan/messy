from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from application.models import Application
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def apply_for_messcut(request):
	application = Application.objects.filter(applicant=request.user).first()
	messcuts = application.messcuts.filter(start_date__month=date.today().month)
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

	return render(request, 'mess/apply.html', {'form': form, 'total_messcut_days': total_messcut_days, 'messcuts': messcuts})


@csrf_exempt
def mark_attendance(request):
	if request.method == 'POST':
		qr_code_data = request.POST.get('qr_code_data')

		try:
			qr_code_data = int(qr_code_data)
		except ValueError:
			return HttpResponse("Invalid QR Code")

		# Find the application using the mess_no from the QR code
		application = Application.objects.filter(mess_no=qr_code_data).first()
		messcuts = application.messcuts.all()
		if application:
			if messcuts:
				for messcut in messcuts:
					if messcut.start_date <= date.today() <= messcut.end_date:
						return HttpResponse("You cannot mark attendance during a messcut period")
			else:
				# Create the attendance record, linking it to the current user
				try:
					attendance = MessAttendance.objects.create(student=application)
					attendance.save()
				except Exception as e:
					return HttpResponse(f"Attendance already marked {e}")
				return HttpResponse("Attendance marked successfully")
		else:
			return HttpResponse("Application not found")

	return render(request, 'mess/scan_qr.html')


def dashboard(request):
	application = Application.objects.filter(applicant=request.user).first()
	return render(request, 'mess/dashboard.html', {'application': application})


def calculate_mess_bill():
	# Constants
	MONTH = date.today()
	AMOUNT_PER_DAY = 90
	ESTABLISHMENT_CHARGES = 300
	TOTAL_DAYS = 30
	OTHER_CHARGES = 0
	FEAST_CHARGES = 0

	for application in Application.objects.filter(accepted=True):

		# Calculate the total amount
		messcuts = application.messcuts.filter(start_date__month=date.today().month)
		total_messcut_days = sum((messcut.end_date - messcut.start_date).days + 1 for messcut in messcuts)
		effective_days = TOTAL_DAYS - total_messcut_days
		total_amount = (AMOUNT_PER_DAY * effective_days) + (ESTABLISHMENT_CHARGES + OTHER_CHARGES+FEAST_CHARGES)
		mess_bill = application.mess_bill.create(
			amount=total_amount,
			month=MONTH,
			paid=False,
			effective_days=effective_days,
			amount_per_day=AMOUNT_PER_DAY,
			establishment_charges=ESTABLISHMENT_CHARGES,
			other_charges=OTHER_CHARGES,
			feast_charges=FEAST_CHARGES,
			total_days=TOTAL_DAYS,
			mess_cuts=total_messcut_days
		)
		# Add the mess cuts to the mess_bill's messcuts field
		mess_bill.mess_cut.add(*messcuts)

		# Save the application
		application.save()

def view_mess_bill(request):
	application = Application.objects.filter(applicant=request.user).first()
	mess_bill = application.mess_bill.filter(month__month=date.today().month).last()
	return render(request, 'mess/view_mess_bill.html', {'mess_bill': mess_bill})