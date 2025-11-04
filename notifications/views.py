from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Notification

@login_required
@never_cache
def list_notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notes, 15)  # 15 notifications par page
    page = request.GET.get('page', 1)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)
    return render(request, 'notifications/list.html', {'notifications': notifications})
