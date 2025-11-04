from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from accounts.models import Account, Card
from notifications.models import Notification
from transactions.models import Transaction
from django.http import JsonResponse
import random
import time
import requests
import json
from django.utils import timezone
from sphinx.email_utils import send_email


def login_view(request):
    # Always force fresh login flow
    if request.user.is_authenticated:
        for k in ['otp_code', 'otp_expires_at', 'otp_attempts', 'otp_verified', 'otp_user_id', 'login_username']:
            if k in request.session:
                del request.session[k]
        logout(request)
    # Step 1: collect username
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if not username:
            messages.error(request, "Veuillez entrer votre identifiant")
        else:
            request.session['login_username'] = username
            return redirect('login_password')
    return render(request, 'accounts/login_step1.html')


def login_password(request):
    username = request.session.get('login_username', '')
    if not username:
        return redirect('login')
    if request.method == 'POST':
        # Clean password: remove all whitespace and invisible characters
        password = request.POST.get('password', '').strip()
        # Remove any remaining invisible characters (non-breaking spaces, etc.)
        password = ''.join(password.split())
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            code = f"{random.randint(0, 99999):05d}"
            request.session['otp_code'] = code
            request.session['otp_user_id'] = user.id
            # OTP metadata: expiry (5 min) and attempts reset
            request.session['otp_expires_at'] = int(time.time()) + 300
            request.session['otp_attempts'] = 0
            send_email(
                subject='Code de vérification (5 chiffres)',
                message=f'Votre code de vérification est: {code}',
                to=[user.email] if user.email else [],
                fail_silently=False,
                html_template='emails/otp_code.html',
                context={'code': code},
            )
            messages.info(request, "Un code à 5 chiffres a été envoyé par email.")
            return redirect('otp_verify')
        messages.error(request, 'Mot de passe invalide')
        # Send security alert if username exists and has email
        try:
            target = User.objects.get(username=username)
            if target.email:
                send_email(
                    subject='Alerte connexion: échec de mot de passe',
                    message='Une tentative de connexion a échoué pour votre compte.',
                    to=[target.email],
                    fail_silently=True,
                    html_template='emails/login_failed.html',
                    context={'timestamp': timezone.now().strftime('%d/%m/%Y à %H:%M')},
                )
        except User.DoesNotExist:
            pass
    return render(request, 'accounts/login_step2.html', {'username': username})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@never_cache
def otp_verify(request):
    if request.session.get('otp_verified'):
        return redirect('dashboard')

    # If no OTP session exists but user is logged in, generate a new one
    if 'otp_code' not in request.session and 'otp_user_id' not in request.session:
        user = request.user
        code = f"{random.randint(0, 99999):05d}"
        request.session['otp_code'] = code
        request.session['otp_user_id'] = user.id
        request.session['otp_expires_at'] = int(time.time()) + 300
        request.session['otp_attempts'] = 0
        send_email(
            subject='Code de vérification (5 chiffres)',
            message=f'Votre code de vérification est: {code}',
            to=[user.email] if user.email else [],
            fail_silently=False,
            html_template='emails/otp_code.html',
            context={'code': code},
        )
        messages.info(request, "Un code à 5 chiffres a été envoyé par email.")

    # Resend code if requested
    if request.method == 'GET' and request.GET.get('resend') == '1':
        user_id = request.session.get('otp_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                code = f"{random.randint(0, 99999):05d}"
                request.session['otp_code'] = code
                request.session['otp_expires_at'] = int(time.time()) + 300
                request.session['otp_attempts'] = 0
                send_email(
                    subject='Nouveau code de vérification',
                    message=f'Nouveau code: {code}',
                    to=[user.email] if user.email else [],
                    fail_silently=False,
                    html_template='emails/otp_code.html',
                    context={'code': code},
                )
                messages.info(request, 'Nouveau code envoyé par email.')
            except User.DoesNotExist:
                messages.error(request, 'Session invalide. Veuillez vous reconnecter.')
                return redirect('login')

    if request.method == 'POST':
        # OTP expiry and attempts control
        expires_at = request.session.get('otp_expires_at')
        now_ts = int(time.time())
        if not expires_at or now_ts > int(expires_at):
            messages.error(request, 'Code expiré. Renvoyez un nouveau code.')
            return redirect('otp_verify')
        attempts = int(request.session.get('otp_attempts') or 0)
        if attempts >= 5:
            # Too many tries; reset login
            for k in ['otp_code', 'otp_expires_at', 'otp_attempts', 'otp_verified', 'otp_user_id', 'login_username']:
                if k in request.session:
                    del request.session[k]
            messages.error(request, "Trop de tentatives. Veuillez vous reconnecter.")
            return redirect('login')
        code = request.POST.get('code', '').strip()
        if code and code == request.session.get('otp_code'):
            request.session['otp_verified'] = True
            # Login success confirmation
            try:
                user = request.user
                if user.email:
                    send_email(
                        subject='Connexion réussie',
                        message='Connexion réussie à votre espace en ligne.',
                        to=[user.email],
                        fail_silently=True,
                        html_template='emails/login_success.html',
                        context={'timestamp': timezone.now().strftime('%d/%m/%Y à %H:%M')},
                    )
            except Exception:
                pass
            messages.success(request, 'Vérification réussie.')
            return redirect('dashboard')
        # wrong code path
        request.session['otp_attempts'] = attempts + 1
        messages.error(request, 'Code invalide.')
    return render(request, 'accounts/otp.html')


@login_required
@never_cache
def dashboard(request):
    if not request.session.get('otp_verified'):
        return redirect('otp_verify')
    user: User = request.user
    account = getattr(user, 'account', None)
    txs = Transaction.objects.filter(owner=user)[:5]
    notes = Notification.objects.filter(user=user, is_read=False)[:5]
    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'transactions': txs,
        'notifications': notes,
    })


@login_required
@never_cache
def rib(request):
    if not request.session.get('otp_verified'):
        return redirect('otp_verify')
    user: User = request.user
    account = getattr(user, 'account', None)
    if not account:
        messages.error(request, "Compte introuvable.")
        return redirect('dashboard')
    # Ensure banking details exist (generated on save if missing)
    if not (account.account_number and account.institution_number and account.transit_number):
        account.save()
    return render(request, 'accounts/rib.html', {'account': account, 'user': user})


@login_required
@never_cache
def card(request):
    if not request.session.get('otp_verified'):
        return redirect('otp_verify')
    user: User = request.user
    account = getattr(user, 'account', None)
    if not account:
        messages.error(request, "Compte introuvable.")
        return redirect('dashboard')
    # Create card if it doesn't exist - Format canadien Visa
    card_obj, created = Card.objects.get_or_create(
        account=account,
        defaults={
            # Visa canadien : commence par 4, format 16 chiffres
            'card_number': f"4{random.randint(100, 999)}{random.randint(100000000000, 999999999999)}",
            'cardholder_name': account.display_name.upper(),
            'expiry_month': 12,
            'expiry_year': 2028,
            'cvv': f"{random.randint(100, 999)}",
            'card_type': 'VISA',
        }
    )
    return render(request, 'accounts/card.html', {'card': card_obj, 'account': account})


@login_required
@never_cache
def currency_converter(request):
    if not request.session.get('otp_verified'):
        return redirect('otp_verify')
    return render(request, 'accounts/currency_converter.html')


@login_required
def get_exchange_rates(request):
    """API endpoint to fetch real-time exchange rates"""
    try:
        # Using exchangerate-api.com (free, no API key needed for basic rates)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Extract rates for CAD, EUR, USD
        rates = {
            'USD': 1.0,
            'CAD': data.get('rates', {}).get('CAD', 1.35),
            'EUR': data.get('rates', {}).get('EUR', 0.92),
        }
        
        # Calculate cross rates
        # CAD to EUR: CAD/USD * USD/EUR = CAD/EUR
        # EUR to CAD: EUR/USD * USD/CAD = EUR/CAD
        rates['CAD_EUR'] = rates['CAD'] / rates['EUR']
        rates['EUR_CAD'] = rates['EUR'] / rates['CAD']
        rates['USD_CAD'] = rates['CAD']
        rates['USD_EUR'] = rates['EUR']
        rates['CAD_USD'] = 1 / rates['CAD']
        rates['EUR_USD'] = 1 / rates['EUR']
        
        return JsonResponse({
            'success': True,
            'rates': rates,
            'timestamp': data.get('date', ''),
            'base': 'USD'
        })
    except requests.RequestException as e:
        # Fallback rates if API fails
        return JsonResponse({
            'success': False,
            'rates': {
                'USD': 1.0,
                'CAD': 1.35,
                'EUR': 0.92,
                'CAD_EUR': 1.467,
                'EUR_CAD': 0.681,
                'USD_CAD': 1.35,
                'USD_EUR': 0.92,
                'CAD_USD': 0.741,
                'EUR_USD': 1.087,
            },
            'error': str(e),
            'timestamp': time.strftime('%Y-%m-%d')
        })
