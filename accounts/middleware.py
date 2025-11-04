from django.shortcuts import redirect
from django.urls import reverse


class OTPRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow anonymous or already verified
        if request.user.is_authenticated:
            otp_verified = request.session.get('otp_verified', False)
            path = request.path
            allowed_paths = {
                reverse('login'),
                reverse('login_password'),
                reverse('otp_verify'),
                reverse('logout'),
            }
            # If authenticated but not OTP-verified, only allow auth/otp/logout paths
            if not otp_verified and path not in allowed_paths and not path.startswith('/admin/'):
                # Always redirect to OTP verification (it will generate a new code if needed)
                return redirect('otp_verify')

        response = self.get_response(request)
        return response


