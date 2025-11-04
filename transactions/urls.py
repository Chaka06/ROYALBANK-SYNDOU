from django.urls import path
from . import views

urlpatterns = [
    path('', views.history, name='transactions_history'),
    path('<int:transaction_id>/', views.detail, name='transaction_detail'),
]
