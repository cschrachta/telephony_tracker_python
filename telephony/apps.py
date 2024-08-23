from django.apps import AppConfig


class TelephonyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telephony"

    def ready(self):
        import telephony.signals  # Import the signals module