from django.contrib import admin
from django.core.management import call_command
from django.utils.safestring import mark_safe

from .models import BlacklistedJWTToken, Device, DeviceImage, Session


class BlacklistedJWTTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "created_at")
    actions = ["flush_old_blacklisted_jwt_tokens"]

    def flush_old_blacklisted_jwt_tokens(self, request, queryset):
        call_command("flush_old_blacklisted_jwt_tokens")
        self.message_user(request, "Flushed blacklisted JWT tokens successfully.")

    flush_old_blacklisted_jwt_tokens.short_description = "Flush blacklisted JWT tokens"

    # Override the changelist_view method to bypass the "no items selected" validation
    def changelist_view(self, request, extra_context=None):
        """
        Override the default behavior to allow running the custom command
        without explicitly selecting any items.
        """
        if (
            "action" in request.POST
            and request.POST["action"] == "flush_old_blacklisted_jwt_tokens"
        ):
            # Modify the queryset to include all items
            queryset = self.get_queryset(request)
            self.flush_old_blacklisted_jwt_tokens(request, queryset)
            # Redirect to the changelist after running the command
            return self.response_post_save_change(request, None)

        return super().changelist_view(request, extra_context=extra_context)


class DeviceImageAdmin(admin.ModelAdmin):
    list_display = ("description", "get_image_preview", "created_at", "updated_at")
    readonly_fields = (
        "get_image_preview",
        "created_at",
        "updated_at",
    )

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                '<img src="{}" '
                'width="100" '
                'height="100" '
                'style="object-fit:contain" />'.format(obj.get_image)
            )
        else:
            return "(No image)"


class SessionInline(admin.TabularInline):
    model = Session
    extra = 0

    readonly_fields = (
        "token",
        "city",
        "country",
        "created_at",
        "updated_at",
    )


class SessionAdmin(admin.ModelAdmin):
    readonly_fields = (
        "token",
        "city",
        "country",
        "created_at",
        "updated_at",
    )


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "get_name",
        "get_image_preview",
        "get_user",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "get_image_preview",
        "created_at",
        "updated_at",
    )
    exclude = ("image",)
    actions = ["flush_expired_tokens_and_devices"]
    inlines = [SessionInline]

    def get_name(self, obj):
        return str(obj)

    def get_user(self, obj):
        return obj.user

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                '<img src="{}" '
                'width="100" '
                'height="100" '
                'style="object-fit:contain" />'.format(obj.get_image)
            )
        else:
            return "(No image)"

    def flush_expired_tokens_and_devices(self, request, queryset):
        call_command("flushexpiredtokens")
        self.message_user(request, "Flushed expired tokens and corresponding devices.")

    # Override the changelist_view method to bypass the "no items selected" validation
    def changelist_view(self, request, extra_context=None):
        """
        Override the default behavior to allow running the custom command
        without explicitly selecting any items.
        """
        if (
            "action" in request.POST
            and request.POST["action"] == "flush_expired_tokens_and_devices"
        ):
            # Modify the queryset to include all items
            queryset = self.get_queryset(request)
            self.flush_expired_tokens_and_devices(request, queryset)
            # Redirect to the changelist after running the command
            return self.response_post_save_change(request, None)

        return super().changelist_view(request, extra_context=extra_context)

    flush_expired_tokens_and_devices.short_description = (
        "Flush expired access tokens and devices"
    )


admin.site.register(BlacklistedJWTToken, BlacklistedJWTTokenAdmin)
admin.site.register(DeviceImage, DeviceImageAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Session, SessionAdmin)
