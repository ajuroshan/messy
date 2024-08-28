from django.shortcuts import render
from django.shortcuts import redirect

from mess.models import MessAttendance, Messcut
from .forms import ApplicationForm
from .models import Application
import datetime
from mess.models import Messmenu
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
	has_applied = Application.objects.filter(applicant=request.user).exists()
	accepted = Application.objects.filter(applicant=request.user, accepted=True).exists()
	application = Application.objects.filter(applicant=request.user).first()
	mess_assistant = request.user.groups.filter(name='mess_assistants').exists()

	today = datetime.datetime.now().strftime('%A').lower()  # Get today's day in lowercase
	menu_today = Messmenu.objects.filter(day=today).first()
	weekly_menu = Messmenu.objects.all().order_by('day')  # Get the full week's menu

	context = {
		'date': datetime.datetime.now().date(),
		'menu_today' : menu_today,
		'weekly_menu': weekly_menu,
		'has_applied': has_applied,
		'accepted': accepted,
		'application': application,
		'mess_assistant': mess_assistant
	}
	return render(request, 'application/home.html', context)

@login_required
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


def login(request):
	return render(request, 'application/login.html')