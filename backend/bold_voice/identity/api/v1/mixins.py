from abc import abstractmethod
from typing import Any, Dict

from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from bold_voice.identity.models import User
from bold_voice.identity.tokens import VerificationTokenGenerator


class VerificationTokenValidationMixin:
    """A mixin to handle the common logic for verification token validation."""

    @abstractmethod
    def get_token_generator(self) -> VerificationTokenGenerator:
        raise NotImplementedError('The `get_token_generator` method must be implemented.')

    def validate_user(self, attrs: Dict[str, Any]) -> User:
        try:
            uid = urlsafe_base64_decode(attrs['uid']).decode()
            user = User.objects.get(pk=uid)
        except Exception as exc:
            raise serializers.ValidationError({'uid': str(exc)})

        token_generator = self.get_token_generator()
        is_valid_token = token_generator.check_token(user=user, token=attrs['token'])
        if not is_valid_token:
            raise serializers.ValidationError({'token': _('Invalid token.')})

        return user
