# src/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect


class SecureMiddleware(MiddlewareMixin):
    """Middleware to redirect all HTTP requests to HTTPS."""

    def process_request(self, request):
        """Redirect to HTTPS if the request is not secure."""
        if not request.is_secure():
            secure_url = f'https://{request.get_host()}{request.get_full_path()}'
            return HttpResponsePermanentRedirect(secure_url)