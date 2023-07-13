from django.contrib import admin
from .models import UserSupportMessage

# Register your models here.
from .models import Contact
from django.contrib import admin
from .models import UserSupportMessage

class UserSupportMessageAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'message_text', 'message_id']
    list_filter = ['chat_id']
    search_fields = ['message_text']

# Регистрация модели в админке
admin.site.register(UserSupportMessage, UserSupportMessageAdmin)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass

