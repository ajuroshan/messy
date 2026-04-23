import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Application, Department, Hostel, Profile


class HostelPaymentBlockMiddlewareTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media_root = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls.temp_media_root)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls.temp_media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.department = Department.objects.create(name="CSE")

    def create_user_with_application(self, username, hostel_name, hostel_code):
        mess_sec = User.objects.create_user(
            username=f"{username}_sec", password="password123"
        )
        hostel = Hostel.objects.create(
            name=hostel_name,
            code=hostel_code,
            mess_sec=mess_sec,
        )
        user = User.objects.create_user(username=username, password="password123")
        Profile.objects.create(user=user)
        Application.objects.create(
            applicant=user,
            first_name="Test",
            last_name="User",
            hostel=hostel,
            accepted=True,
            department=self.department,
            semester="S1",
            student_id=f"{username}-id",
            phone_number="9999999999",
        )
        return user

    def test_sahara_user_sees_payment_page_on_home(self):
        user = self.create_user_with_application("sahara_user", "Sahara", "SGR")
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertContains(response, "503 Service Unavailable")
        self.assertContains(response, "ServiceSuspended.PaymentPending")

    def test_sanathana_user_is_blocked_on_mess_routes(self):
        user = self.create_user_with_application("sanathana_user", "Sanathana", "SNT")
        self.client.force_login(user)

        response = self.client.get("/mess/dashboard/")

        self.assertContains(response, "503 Service Unavailable")
        self.assertContains(response, "pending payment")

    def test_other_hostel_user_can_access_home(self):
        user = self.create_user_with_application("sagar_user", "Sagar", "SGR")
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertContains(response, "No menu available for today.")
        self.assertNotContains(response, "ServiceSuspended.PaymentPending")
