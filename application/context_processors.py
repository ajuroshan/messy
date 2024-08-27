from .models import Application

def global_variables(request):
    if request.user.is_authenticated:
        has_verified_application = Application.objects.filter(applicant=request.user, accepted=True).exists()
    else:
        has_verified_application = False

    return {
        'has_verified_application': has_verified_application,
        # Add more variables here if needed
    }