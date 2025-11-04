from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Transaction

@login_required
@never_cache
def history(request):
    txs = Transaction.objects.filter(owner=request.user)
    paginator = Paginator(txs, 10)  # 10 transactions par page
    page = request.GET.get('page', 1)
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    return render(request, 'transactions/history.html', {'transactions': transactions})

@login_required
@never_cache
def detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # Security: ensure transaction belongs to current user
    if transaction.owner != request.user:
        raise Http404("Transaction introuvable")
    return render(request, 'transactions/detail.html', {'transaction': transaction})
