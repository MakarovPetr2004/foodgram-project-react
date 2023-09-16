from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active'
    )
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


admin.site.register(User, CustomUserAdmin)
