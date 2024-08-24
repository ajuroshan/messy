from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from application.models import Application
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def apply_for_messcut(request):
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

	return render(request, 'mess/apply.html', {'form': form})


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

		if application:
			# Create the attendance record, linking it to the current user
			attendance = MessAttendance.objects.create(student=application)
			attendance.save()
			return HttpResponse("Attendance marked successfully")
		else:
			return HttpResponse("Application not found")

	return render(request, 'mess/scan_qr.html')
