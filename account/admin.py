from account.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


UserAdmin.fieldsets[1][1]['fields'] += ('phone', 'telegram_id', 'instagram_id')
UserAdmin.list_display = ('name', 'telegram_id', 'instagram_id', 'is_verified')

admin.site.register(User, UserAdmin)
