from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_alt'),  # Alias pour /login/
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rib/', views.rib, name='rib'),
    # path('card/', views.card, name='card'),  # Card feature removed
    path('currency/', views.currency_converter, name='currency_converter'),
    path('api/exchange-rates/', views.get_exchange_rates, name='get_exchange_rates'),
    path('login/password/', views.login_password, name='login_password'),
    path('logout/', views.logout_view, name='logout'),
    path('otp/', views.otp_verify, name='otp_verify'),
]
