from abc import abstractmethod
from typing import Any, Dict, Optional

from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.request import Request

from bold_voice.common.api.fields import PasswordField
from bold_voice.common.api.types import ResponseData
from bold_voice.identity.api.v1.mixins import VerificationTokenValidationMixin
from bold_voice.identity.models import User
from bold_voice.identity.services import PasswordResetService
from bold_voice.identity.tokens import VerificationTokenGenerator


class PasswordSerializer(serializers.Serializer):
    """A base class to handle the common logic for password-related serializers."""

    password = PasswordField(label=_('Password'), write_only=True)
    confirm_password = PasswordField(label=_('Confirm password'), write_only=True)
    status = serializers.CharField(label=_('Status'), read_only=True)

    @property
    def _response_data(self) -> ResponseData:
        return {'status': _('Password has been changed.')}

    @abstractmethod
    def validate_user(self, attrs: Dict[str, Any]) -> User:
        raise NotImplementedError('The `set_user_instance` method must be implemented.')

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # Store the user instance for later use in the `update` method.
        self.instance = self.validate_user(attrs=attrs)

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})

        try:
            validate_password(password=attrs['password'], user=self.instance)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})
        except Exception as exc:
            raise serializers.ValidationError({'password': str(exc)})

        return attrs

    def update(self, instance: User, validated_data):
        instance.set_password(raw_password=validated_data['password'])
        instance.save(update_fields=['password'])
        return self._response_data


class PasswordResetConfirmSerializer(VerificationTokenValidationMixin, PasswordSerializer):
    uid = serializers.CharField(label=_('UID'), write_only=True)
    token = serializers.CharField(label=_('Token'), write_only=True)

    def get_token_generator(self) -> VerificationTokenGenerator:
        return PasswordResetService.token_generator


class PasswordChangeSerializer(PasswordSerializer):
    old_password = PasswordField(label=_('Old password'), write_only=True)

    def validate_user(self, attrs: Dict[str, Any]) -> User:
        user: User = self.context['request'].user
        if not check_password(attrs['old_password'], user.password):
            raise serializers.ValidationError({'old_password': _('Incorrect password.')})

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_('Email address'), write_only=True)
    status = serializers.CharField(label=_('Status'), read_only=True)

    @property
    def _response_data(self) -> ResponseData:
        return {'status': _('Password reset email has been sent.')}

    def create(self, validated_data):
        request: Request = self.context['request']
        user: Optional[User] = User.objects.filter(email=validated_data['email']).first()

        if not user or not user.has_usable_password():
            # Do not reveal whether the email address is valid or not
            return self._response_data

        PasswordResetService(user=user, request=request).send()
        return self._response_data
