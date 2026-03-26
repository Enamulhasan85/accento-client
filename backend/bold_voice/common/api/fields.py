from rest_framework import serializers


class PasswordField(serializers.CharField):
    """Custom serializer field for password input."""

    def __init__(self, **kwargs):
        # Set default style and write_only properties
        kwargs.setdefault('style', {})

        kwargs['max_length'] = 128  # Django's default
        kwargs['write_only'] = True
        kwargs['style']['input_type'] = 'password'

        super().__init__(**kwargs)
