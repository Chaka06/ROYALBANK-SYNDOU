from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.contrib.auth.models import User
from sphinx.email_utils import send_email

signer = TimestampSigner()

@login_required
@never_cache
def profile(request):
    return render(request, 'profiles/profile.html')

@login_required
@never_cache
def email_change_request(request):
    if request.method == 'POST':
        new_email = request.POST.get('email', '').strip()
        if not new_email:
            messages.error(request, "Veuillez saisir un email valide")
        else:
            token = signer.sign(f"{request.user.id}:{new_email}")
            verify_url = f"{getattr(settings,'SITE_URL','')}/profiles/email/verify/{token}/"
            # Optional: ensure email is not already used by another account
            if User.objects.filter(email__iexact=new_email).exclude(id=request.user.id).exists():
                messages.error(request, "Cette adresse email est déjà utilisée.")
                return render(request, 'profiles/email_change_request.html')
            send_email(
                subject='Vérification de la nouvelle adresse email',
                message=f'Pour confirmer votre nouvelle adresse, cliquez: {verify_url}',
                to=[new_email],
                fail_silently=False,
                html_template='emails/email_verification.html',
                context={'verify_url': verify_url},
            )
            messages.success(request, 'Un email de vérification a été envoyé à la nouvelle adresse.')
            return redirect('profile')
    return render(request, 'profiles/email_change_request.html')

@login_required
@never_cache
def email_change_verify(request, token: str):
    try:
        raw = signer.unsign(token, max_age=3600)
        user_id, new_email = raw.split(':', 1)
        if str(request.user.id) != user_id:
            messages.error(request, "Jeton invalide.")
            return redirect('profile')
        request.user.email = new_email
        request.user.save()
        messages.success(request, 'Adresse email mise à jour avec succès.')
    except SignatureExpired:
        messages.error(request, 'Lien expiré, veuillez refaire la demande.')
    except BadSignature:
        messages.error(request, 'Jeton invalide.')
    return redirect('profile')
