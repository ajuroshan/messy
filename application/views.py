from django.shortcuts import render
from django.shortcuts import redirect

from mess.models import MessAttendance, Messcut
from .forms import ApplicationForm
from .models import Application

# Create your views here.

def home(request):
	has_applied = Application.objects.filter(applicant=request.user).exists()
	accepted = Application.objects.filter(applicant=request.user, accepted=True).exists()
	return render(request, 'application/home.html', {'has_applied': has_applied, 'accepted': accepted})


def apply(request):
	if request.method == 'POST':
		form = ApplicationForm(request.POST)
		if form.is_valid():
			application = form.save(commit=False)
			application.applicant = request.user
			application.save()
			return redirect('home')
	else:
		form = ApplicationForm()

	return render(request, 'application/apply.html', {'form': form})



def calculate_mess_bill(request):
	# Constants
	MONTH = 6
	AMOUNT_PER_DAY = 10
	ESTABLISHMENT_CHARGES = 50
	TOTAL_DAYS = 30

	for application in Application.objects.filter(accepted=True):
		# Calculate the total amount
		mess_cuts = application.messcuts.filter(start_date__month=MONTH).count()
		effective_days = TOTAL_DAYS - mess_cuts
		total_amount = (AMOUNT_PER_DAY * effective_days) + ESTABLISHMENT_CHARGES
		application.mess_bill.create(total_amount=total_amount, month=MONTH, paid=False)
		application.save()



