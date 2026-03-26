from typing import Any, Dict

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.request import Request

from bold_voice.identity import tokens
from bold_voice.identity.models import User
from bold_voice.identity.tasks import send_generic_email

# Type alias for the context used in rendering email templates.
EmailContext = Dict[str, Any]


class EmailService:
    """A base class to handle the common logic for email services."""

    subject_template = None
    body_template = None
    token_generator = None
    client_url = None

    def __init__(self, user: User, request: Request, **kwargs):
        self.user = user
        self.request = request
        self.kwargs = kwargs

    def get_context(self) -> EmailContext:
        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = self.token_generator.make_token(self.user)

        context = {
            'site_name': current_site.name,
            'action_link': f'{self.client_url}?uid={uid}&token={token}',
        }
        context.update(self.kwargs)  # Allow additional context
        return context

    def get_subject(self, context: EmailContext) -> str:
        subject = loader.render_to_string(self.subject_template, context)
        return ''.join(subject.splitlines())  # Remove newlines from subject

    def get_body(self, context: EmailContext) -> str:
        return loader.render_to_string(self.body_template, context)

    def dispatch_email(self, subject, message, recipients):
        send_generic_email.delay(subject=subject, message=message, recipients=recipients)

    def send(self) -> None:
        """Sends the email using the subject and body templates and the provided context."""
        context = self.get_context()
        subject = self.get_subject(context)
        body = self.get_body(context)
        self.dispatch_email(subject=subject, message=body, recipients=[self.user.email])


class EmailConfirmationService(EmailService):
    subject_template = 'identity/email_confirmation_subject.txt'
    body_template = 'identity/email_confirmation_email.html'
    token_generator = tokens.email_confirmation_token_generator
    client_url = settings.FRONTEND_EMAIL_CONFIRMATION_URL


class PasswordResetService(EmailService):
    subject_template = 'identity/password_reset_subject.txt'
    body_template = 'identity/password_reset_email.html'
    token_generator = tokens.password_reset_token_generator
    client_url = settings.FRONTEND_PASSWORD_RESET_URL
