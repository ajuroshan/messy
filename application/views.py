from django.shortcuts import render
from django.shortcuts import redirect
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