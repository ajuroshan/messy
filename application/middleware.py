from django.conf import settings
from django.shortcuts import render

from .access import is_payment_blocked_user


class HostelPaymentBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_prefixes = (
            settings.STATIC_URL,
            settings.MEDIA_URL,
            "/accounts/",
        )
        self.exempt_paths = {
            "/login/",
        }

    def __call__(self, request):
        if self._is_exempt_path(request.path):
            return self.get_response(request)

        if is_payment_blocked_user(request.user):
            return render(request, "application/aws_payment.html")

        return self.get_response(request)

    def _is_exempt_path(self, path):
        if path in self.exempt_paths:
            return True

        return any(prefix and path.startswith(prefix) for prefix in self.exempt_prefixes)
