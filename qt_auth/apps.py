from django.apps import AppConfig


class QtAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "qt_auth"
    verbose_name = "Authentication"

    def ready(self):
        # import signals in order to use them
        import qt_auth.signals  # noqa
