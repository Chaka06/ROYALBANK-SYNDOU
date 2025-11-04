from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as django_messages
from .models import ChatThread, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'content', 'created_at')
    can_delete = False
    fields = ('sender', 'content', 'created_at')
    
    def has_add_permission(self, request, obj=None):
        # Ne pas permettre d'ajouter via inline, utiliser la vue personnalisée
        return False

@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "is_closed", "message_count", "reply_action")
    list_filter = ("is_closed", "created_at")
    readonly_fields = ('id', 'user', 'created_at', 'messages_display')
    search_fields = ('user__username', 'user__email')
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"
    
    def reply_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Répondre</a>',
            f'/admin/support/chatthread/{obj.id}/reply/'
        )
    reply_action.short_description = "Actions"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:thread_id>/reply/',
                self.admin_site.admin_view(self.reply_view),
                name='support_chatthread_reply',
            ),
        ]
        return custom_urls + urls
    
    def reply_view(self, request, thread_id):
        """Vue personnalisée pour répondre aux messages"""
        thread = get_object_or_404(ChatThread, id=thread_id)
        messages_list = thread.messages.all().order_by('created_at')
        
        if request.method == 'POST':
            content = request.POST.get('reply_content', '').strip()
            if content:
                ChatMessage.objects.create(
                    thread=thread,
                    sender='admin',
                    content=content
                )
                django_messages.success(request, 'Réponse envoyée avec succès!')
                return redirect(f'/admin/support/chatthread/{thread_id}/reply/')
            else:
                django_messages.error(request, 'Le message ne peut pas être vide.')
        
        context = {
            'title': f'Répondre à la discussion #{thread.id}',
            'thread': thread,
            'messages': messages_list,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, thread),
            'has_change_permission': self.has_change_permission(request, thread),
        }
        return render(request, 'admin/support/reply_thread.html', context)
    
    def messages_display(self, obj):
        """Affiche tous les messages dans le détail"""
        messages = obj.messages.all().order_by('created_at')
        html = '<div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background: #f9f9f9;">'
        for msg in messages:
            sender_class = 'user' if msg.sender == 'user' else 'admin'
            sender_label = 'Utilisateur' if msg.sender == 'user' else 'Support'
            html += f'''
                <div style="margin-bottom: 15px; padding: 10px; background: {'#e3f2fd' if sender_class == 'admin' else '#fff'}; border-left: 3px solid {'#0047bb' if sender_class == 'admin' else '#666'};">
                    <strong>{sender_label}</strong> - {msg.created_at.strftime("%d/%m/%Y %H:%M")}<br>
                    <div style="margin-top: 5px;">{msg.content}</div>
                </div>
            '''
        html += '</div>'
        return format_html(html)
    messages_display.short_description = "Messages"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "sender", "content_preview", "created_at")
    list_filter = ("sender", "created_at")
    readonly_fields = ("thread", "sender", "content", "created_at")
    search_fields = ("content", "thread__user__username")
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Contenu"
    
    def has_add_permission(self, request):
        # Utiliser la vue de réponse pour ajouter des messages admin
        return False
