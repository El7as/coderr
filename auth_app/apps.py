from django.apps import AppConfig


class AuthAppConfig(AppConfig):

    """
    Application configuration for the authentication app.

    This class registers the `auth_app` Django application and allows
    Django to initialize any app-specific settings, signals, or startup
    logic when the project loads.

    Attributes:
        name (str):
            The dotted Python path to the application. Django uses this
            to locate the app and its components.
    """

    name = 'auth_app'
