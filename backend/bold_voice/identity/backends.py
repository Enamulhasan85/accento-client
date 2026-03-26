from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from bold_voice.identity.models import User


class UsernameOrEmailAuthBackend(ModelBackend):
    """Authenticate a user by username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        username = username or kwargs.get('username')
        email = kwargs.get('email')

        if not password or not (username or email):
            return

        expr = Q(username=username)
        if email is not None:
            expr = Q(email=email)

        try:
            user = User.objects.get(expr)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(raw_password=password)
        else:
            if (
                    user.check_password(raw_password=password) and
                    self.user_can_authenticate(user)
            ):
                return user
