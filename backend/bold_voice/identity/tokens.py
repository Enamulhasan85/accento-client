from django.contrib.auth.tokens import PasswordResetTokenGenerator


class VerificationTokenGenerator(PasswordResetTokenGenerator):
    """A base class to handle the common logic for verification token generators."""


class EmailConfirmationTokenGenerator(VerificationTokenGenerator):
    """This class is used to generate a token for email confirmation."""

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.email}'


class PasswordResetTokenGenerator(VerificationTokenGenerator):
    """This class is used to generate a token for password reset."""

    def _make_hash_value(self, user, timestamp):
        return super()._make_hash_value(user, timestamp)


email_confirmation_token_generator = EmailConfirmationTokenGenerator()
password_reset_token_generator = PasswordResetTokenGenerator()
