from django.shortcuts import redirect


class OTPRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Utiliser des chemins en dur au lieu de reverse() pour éviter
        # les problèmes d'initialisation.
        # Les chemins correspondent aux URLs définies dans accounts/urls.py
        self.allowed_paths = {
            '/',              # login
            '/login/',        # login_alt
            '/login/password/',  # login_password
            '/otp/',          # otp_verify
            '/logout/',       # logout
        }

    def __call__(self, request):
        # Allow anonymous or already verified
        if request.user.is_authenticated:
            otp_verified = request.session.get('otp_verified', False)
            path = request.path
            # If authenticated but not OTP-verified,
            # only allow auth/otp/logout paths
            if (not otp_verified and path not in self.allowed_paths and
                    not path.startswith('/admin/')):
                # Always redirect to OTP verification
                # (it will generate a new code if needed)
                return redirect('otp_verify')

        response = self.get_response(request)
        return response


