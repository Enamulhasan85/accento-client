from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.request import Request

from bold_voice.common.api.types import ResponseData
from bold_voice.identity.api.v1.mixins import VerificationTokenValidationMixin
from bold_voice.identity.models import User
from bold_voice.identity.services import EmailConfirmationService
from bold_voice.identity.tokens import VerificationTokenGenerator


class EmailConfirmSerializer(VerificationTokenValidationMixin, serializers.Serializer):
    token = serializers.CharField(label=_('Token'), write_only=True)
    uid = serializers.CharField(label=_('UID'), write_only=True)
    status = serializers.CharField(label=_('Status'), read_only=True)

    @property
    def _response_data(self) -> ResponseData:
        return {'status': _('Email has been confirmed.')}

    def get_token_generator(self) -> VerificationTokenGenerator:
        return EmailConfirmationService.token_generator

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Store the user instance for later use in the `update` method.
        self.instance = self.validate_user(attrs=attrs)
        return attrs

    def update(self, instance: User, validated_data):
        instance.email_verified = True
        instance.save(update_fields=['email_verified'])
        return self._response_data


class EmailConfirmationResendSerializer(serializers.Serializer):
    status = serializers.CharField(label=_('Status'), read_only=True)

    @property
    def _response_data(self):
        return {'status': _('Confirmation email has been resent.')}

    def validate(self, attrs):
        request: Request = self.context['request']
        if request.user.email_verified:
            raise serializers.ValidationError({'status': _('Email has already been verified.')})

        return super().validate(attrs)

    def create(self, validated_data):
        request: Request = self.context['request']
        user: User = request.user

        EmailConfirmationService(user=user, request=request).send()
        return self._response_data
