from django.contrib import admin
from user.models import User
from user_activity_log.models import UserActivityLog


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserActivityLog)

