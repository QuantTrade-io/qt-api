from django.contrib import admin

from .models import BrokerAuthenticationMethod, Broker, BrokerAccount, Holding


class BrokerAccountAdmin(admin.ModelAdmin):
    model = BrokerAccount
    list_display = ("user", "broker", "username", "email", "authentication_method",)
    exclude = ("password", "int_account", )


# Register your models here.
admin.site.register(BrokerAuthenticationMethod)
admin.site.register(Broker)
admin.site.register(BrokerAccount, BrokerAccountAdmin)
admin.site.register(Holding)