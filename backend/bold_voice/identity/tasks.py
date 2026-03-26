from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from config.celery import app


@app.task(name='email_service.send_generic_email')
def send_generic_email(subject, message, recipients):
    text_content = strip_tags(message)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=recipients
    )

    # Attach HTML version
    email.attach_alternative(message, "text/html")

    return email.send()
