from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from .models import ChatThread, ChatMessage

@login_required
@never_cache
def chat(request):
    thread, _ = ChatThread.objects.get_or_create(user=request.user, is_closed=False)
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            ChatMessage.objects.create(thread=thread, sender='user', content=content)
            return redirect('support_chat')
    messages = list(thread.messages.all())
    return render(request, 'support/chat.html', {'thread': thread, 'messages': messages})
