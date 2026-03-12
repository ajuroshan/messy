from datetime import date, datetime, time, timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageDraw

from application.models import Application, Department, Hostel, Profile
from mess.models import (
    Feedback,
    MessAttendance,
    MessBill,
    MessClosedDate,
    Messcut,
    Messmenu,
    Messsettings,
)


def current_meal(settings):
    now = timezone.localtime().time()
    if settings.breakfast_start_time <= now < settings.breakfast_end_time:
        return "breakfast"
    if settings.lunch_start_time <= now < settings.lunch_end_time:
        return "lunch"
    if settings.dinner_start_time <= now < settings.dinner_end_time:
        return "dinner"
    raise ValueError("Current time is outside the configured mess meal windows.")


def upsert_user(username, email, first_name, last_name, password, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "is_staff": is_staff,
        },
    )
    changed = created
    if user.email != email:
        user.email = email
        changed = True
    if user.first_name != first_name:
        user.first_name = first_name
        changed = True
    if user.last_name != last_name:
        user.last_name = last_name
        changed = True
    if user.is_staff != is_staff:
        user.is_staff = is_staff
        changed = True
    if not user.check_password(password):
        user.set_password(password)
        changed = True
    if changed:
        user.save()
    Profile.objects.get_or_create(user=user)
    return user


def upsert_application(
    applicant,
    hostel,
    department,
    first_name,
    last_name,
    semester,
    food_preference,
    student_id,
    phone_number,
    accepted,
    outmess,
    claim,
    official_outmess,
):
    application = Application.objects.filter(applicant=applicant).first()
    if application is None:
        application = Application(
            applicant=applicant,
            hostel=hostel,
            department=department,
            first_name=first_name,
            last_name=last_name,
            semester=semester,
            food_preference=food_preference,
            student_id=student_id,
            phone_number=phone_number,
            accepted=accepted,
            outmess=outmess,
            claim=claim,
            official_outmess=official_outmess,
        )
        application.save()
        return application

    application.hostel = hostel
    application.department = department
    application.first_name = first_name
    application.last_name = last_name
    application.semester = semester
    application.food_preference = food_preference
    application.student_id = student_id
    application.phone_number = phone_number
    application.accepted = accepted
    application.outmess = outmess
    application.claim = claim
    application.official_outmess = official_outmess
    application.save()
    return application


def ensure_profile_image(application, fill_color):
    image = Image.new("RGB", (320, 320), fill_color)
    draw = ImageDraw.Draw(image)
    initials = f"{application.first_name[:1]}{application.last_name[:1]}".strip() or application.first_name[:1]
    draw.text((130, 145), initials.upper(), fill="white")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    filename = f"profile_{application.applicant.username}.png"
    application.profile_pic.save(filename, ContentFile(buffer.getvalue()), save=False)
    application.save()


mess_sec = upsert_user(
    username="messsec_sagar",
    email="messsec.sagar@example.com",
    first_name="Mess",
    last_name="Secretary",
    password="password123",
    is_staff=True,
)

hostel, _ = Hostel.objects.update_or_create(
    name="Sagar",
    defaults={
        "mess_sec": mess_sec,
        "code": "SGR",
        "assistant_mess_sec": "Anand Kumar",
    },
)

departments = {}
for dept_name in ["Computer Science", "Electronics", "Mechanical"]:
    departments[dept_name], _ = Department.objects.get_or_create(name=dept_name)

today = timezone.localdate()
month_start = today.replace(day=1)
previous_month_end = month_start - timedelta(days=1)
previous_month_start = previous_month_end.replace(day=1)

closed_dates = []
for offset in [5, 12]:
    closed_date, _ = MessClosedDate.objects.get_or_create(date=month_start + timedelta(days=offset))
    closed_dates.append(closed_date)

settings, _ = Messsettings.objects.update_or_create(
    hostel=hostel,
    defaults={
        "total_days": 30,
        "amount_per_day": 120,
        "establishment_charges": 2500,
        "feast_charges": 400,
        "other_charges": 150,
        "mess_secretary_upi_id": "messsec@upi",
        "mess_secretary_upi_id_link": "upi://pay?pa=messsec@upi",
        "sagar_post_metric_upi_id": "sagarpm@upi",
        "sagar_post_metric_upi_id_link": "upi://pay?pa=sagarpm@upi",
        "month_for_bill_calculation": month_start,
        "last_date_for_payment": month_start + timedelta(days=20),
        "per_day_fine_after_due_date": 25,
        "mess_secretary_name": "Rohit",
        "mess_secretary_contact": "9999999999",
        "assistant_mess_secretary_name": "Anand",
        "assistant_mess_secretary_contact": "8888888888",
        "publish_mess_bill": True,
        "breakfast_start_time": time(0, 0, 0),
        "breakfast_end_time": time(8, 0, 0),
        "lunch_start_time": time(8, 0, 0),
        "lunch_end_time": time(16, 0, 0),
        "dinner_start_time": time(16, 0, 0),
        "dinner_end_time": time(23, 59, 59),
        "messcut_closing_time": time(22, 0, 0),
        "mess_closed_days": len(closed_dates),
        "bill_calculation_date": today,
    },
)
settings.mess_closed_dates.set(closed_dates)

menu_items = {
    "monday": ("Idli and sambar", "Rice, dal, and stir fry", "Chapati and paneer curry"),
    "tuesday": ("Poha and banana", "Jeera rice and rajma", "Parotta and kurma"),
    "wednesday": ("Dosa and chutney", "Fried rice and gobi", "Chapati and chicken curry"),
    "thursday": ("Upma and tea", "Rice, sambar, and thoran", "Noodles and chilli paneer"),
    "friday": ("Poori and masala", "Veg biryani and raita", "Chapati and egg curry"),
    "saturday": ("Puttu and kadala", "Rice and fish curry", "Ghee rice and veg kurma"),
    "sunday": ("Appam and stew", "Chicken biryani", "Chapati and dal makhani"),
}
for day, meals in menu_items.items():
    Messmenu.objects.update_or_create(
        day=day,
        defaults={
            "breakfast": meals[0],
            "lunch": meals[1],
            "dinner": meals[2],
        },
    )

student_specs = [
    {
        "username": "alice.student",
        "email": "alice.student@example.com",
        "first_name": "Alice",
        "last_name": "Joseph",
        "department": departments["Computer Science"],
        "semester": "S3",
        "food_preference": "veg",
        "student_id": "SAGAR001",
        "phone_number": "9000000001",
        "accepted": True,
        "outmess": False,
        "claim": True,
        "official_outmess": False,
        "messcut_days": (2, 4),
        "feedback": "Breakfast quality has improved a lot this month.",
        "profile_color": "#3b82f6",
    },
    {
        "username": "bob.student",
        "email": "bob.student@example.com",
        "first_name": "Bob",
        "last_name": "Thomas",
        "department": departments["Electronics"],
        "semester": "S5",
        "food_preference": "nonveg",
        "student_id": "SAGAR002",
        "phone_number": "9000000002",
        "accepted": True,
        "outmess": True,
        "claim": False,
        "official_outmess": True,
        "messcut_days": (10, 13),
        "feedback": "Please keep the dinner timing strict during exams.",
        "profile_color": "#f97316",
    },
    {
        "username": "carol.student",
        "email": "carol.student@example.com",
        "first_name": "Carol",
        "last_name": "Mathew",
        "department": departments["Mechanical"],
        "semester": "S1",
        "food_preference": "veg",
        "student_id": "SAGAR003",
        "phone_number": "9000000003",
        "accepted": False,
        "outmess": False,
        "claim": False,
        "official_outmess": False,
        "messcut_days": (15, 17),
        "feedback": "Need more fruit options at breakfast.",
        "profile_color": "#16a34a",
    },
]

applications = []
active_meal = current_meal(settings)
for spec in student_specs:
    user = upsert_user(
        username=spec["username"],
        email=spec["email"],
        first_name=spec["first_name"],
        last_name=spec["last_name"],
        password="password123",
    )
    application = upsert_application(
        applicant=user,
        hostel=hostel,
        department=spec["department"],
        first_name=spec["first_name"],
        last_name=spec["last_name"],
        semester=spec["semester"],
        food_preference=spec["food_preference"],
        student_id=spec["student_id"],
        phone_number=spec["phone_number"],
        accepted=spec["accepted"],
        outmess=spec["outmess"],
        claim=spec["claim"],
        official_outmess=spec["official_outmess"],
    )
    ensure_profile_image(application, spec["profile_color"])

    messcut, _ = Messcut.objects.get_or_create(
        hostel=hostel,
        start_date=month_start + timedelta(days=spec["messcut_days"][0]),
        end_date=month_start + timedelta(days=spec["messcut_days"][1]),
    )
    application.messcuts.add(messcut)

    attendance = MessAttendance.objects.filter(
        student=application,
        hostel=hostel,
        date=today,
        meal=active_meal,
    ).first()
    if attendance is None:
        attendance = MessAttendance(student=application, hostel=hostel)
        attendance.save()
    application.attendance.add(attendance)

    feedback, created = Feedback.objects.get_or_create(
        student=application,
        feedback=spec["feedback"],
        defaults={"date": today},
    )
    if not created and feedback.feedback != spec["feedback"]:
        feedback.feedback = spec["feedback"]
        feedback.save()

    current_bill, _ = MessBill.objects.update_or_create(
        hostel=hostel,
        month=month_start,
        defaults={
            "total_days": 30,
            "effective_days": 27,
            "amount_per_day": 120,
            "establishment_charges": 2500,
            "feast_charges": 400,
            "other_charges": 150,
            "mess_cuts": 3,
            "effective_mess_cuts": 3,
            "amount": 6290,
            "date_paid": today if spec["accepted"] else None,
            "paid": spec["accepted"],
            "fine_paid": 0,
            "amount_paid": 6290 if spec["accepted"] else 0,
        },
    )
    previous_bill, _ = MessBill.objects.update_or_create(
        hostel=hostel,
        month=previous_month_start,
        defaults={
            "total_days": previous_month_end.day,
            "effective_days": previous_month_end.day - 2,
            "amount_per_day": 115,
            "establishment_charges": 2400,
            "feast_charges": 350,
            "other_charges": 120,
            "mess_cuts": 2,
            "effective_mess_cuts": 2,
            "amount": 5855,
            "date_paid": previous_month_start + timedelta(days=18),
            "paid": True,
            "fine_paid": 0,
            "amount_paid": 5855,
        },
    )
    application.mess_bill.add(current_bill, previous_bill)
    applications.append(application)

print("Seed data ready.")
print(f"Users: {User.objects.count()}")
print(f"Profiles: {Profile.objects.count()}")
print(f"Hostels: {Hostel.objects.count()}")
print(f"Departments: {Department.objects.count()}")
print(f"Applications: {Application.objects.count()}")
print(f"Mess cuts: {Messcut.objects.count()}")
print(f"Menus: {Messmenu.objects.count()}")
print(f"Attendance rows: {MessAttendance.objects.count()}")
print(f"Bills: {MessBill.objects.count()}")
print(f"Feedback rows: {Feedback.objects.count()}")
print(f"Closed dates: {MessClosedDate.objects.count()}")
print(f"Mess settings: {Messsettings.objects.count()}")
print("Created or updated users use password: password123")
