from django.apps import AppConfig


class APIConfig(AppConfig):
    name = "grantnav.api"

    def ready(self):
        # Makes sure all signal handlers are connected
        #logger.error(f"Importing corsheader signal handler")
        from grantnav.api import handlers  # noqa
