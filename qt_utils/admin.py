from django.contrib import admin

from .models import NewsletterSubscriber


class NewsletterSubscriberAdmin(admin.ModelAdmin):
    fields = (
        "email",
        "uuid",
    )
    readonly_fields = ("uuid",)

    class Meta:
        model = NewsletterSubscriber


admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
