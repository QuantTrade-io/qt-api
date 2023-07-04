from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = [
        "customer",
    ]

    class Meta:
        model = User
        fields = "__all__"


admin.site.register(User, UserAdmin)
