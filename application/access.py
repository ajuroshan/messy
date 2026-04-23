from .models import Application


PAYMENT_BLOCKED_HOSTELS = {"sahara"}


def get_verified_application(user):
    if not getattr(user, "is_authenticated", False):
        return None

    return (
        Application.objects.select_related("hostel")
        .filter(applicant=user, accepted=True)
        .first()
    )


def is_payment_blocked_user(user):
    application = get_verified_application(user)

    if not application or not application.hostel_id or not application.hostel.name:
        return False

    return application.hostel.name.strip().casefold() in PAYMENT_BLOCKED_HOSTELS
