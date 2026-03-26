import uuid
from typing import Optional

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken

from bold_voice.common.api.fields import PasswordField
from bold_voice.identity.signals import user_registered
from bold_voice.identity.utils import generate_jwt_token_for_user

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = PasswordField(label=_('Password'), write_only=True)
    confirm_password = PasswordField(label=_('Confirm password'), write_only=True)
    access_token = serializers.CharField(label=_('Access token'), read_only=True)
    refresh_token = serializers.CharField(label=_('Refresh token'), read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'confirm_password',
            'access_token',
            'refresh_token',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # After successful registration, only the `access_token` and `refresh_token` will be returned.
        # To exclude all other fields from the response, we mark them as write-only.
        for field_name in self.fields.keys():
            if field_name in ['access_token', 'refresh_token']:
                continue
            self.fields[field_name].write_only = True

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs['password'] != attrs['confirm_password']:  # noqa
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})

        try:
            validate_password(password=attrs['password'], user=self.instance)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})
        except Exception as exc:
            raise serializers.ValidationError({'password': str(exc)})

        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError({'email': _('User with the provided email already exists.')})

        return attrs

    def create(self, validated_data):
        request: Request = self.context['request']

        validated_data.pop('confirm_password')  # Needed for validation only.

        random_username = uuid.uuid4().hex
        user = User.objects.create_user(username=random_username, **validated_data)

        # Send signal to handle user registration
        user_registered.send(sender=User, user=user, request=request)

        token_data = generate_jwt_token_for_user(user=user)
        return user.__dict__ | token_data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_('Email'), write_only=True)
    password = PasswordField(label=_('Password'), write_only=True)
    access_token = serializers.CharField(label=_('Access token'), read_only=True)
    refresh_token = serializers.CharField(label=_('Refresh token'), read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'access_token', 'refresh_token']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['email'] = attrs['email'].lower()

        user: Optional[User] = authenticate(request=self.context['request'], **attrs)
        if user is None:
            raise AuthenticationFailed(
                detail=_('User not found with the provided credentials.'),
                code='user_not_found'
            )
        elif not user.is_active:
            raise AuthenticationFailed(
                detail=_('The user account is inactive. Please contact support.'),
                code='user_inactive'
            )

        # Store the user instance for later use in the `create` method.
        attrs['user'] = user

        return attrs

    def create(self, validated_data):
        token_data = generate_jwt_token_for_user(user=validated_data['user'])
        return validated_data | token_data


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(label=_('Refresh token'))
    access_token = serializers.CharField(label=_('Access token'), read_only=True)

    class Meta:
        model = User
        fields = ['refresh_token', 'access_token']

    @classmethod
    def validate_refresh_token(cls, value):
        try:
            refresh_token = RefreshToken(token=value)
        except Exception as exc:
            raise serializers.ValidationError({'refresh_token': str(exc)})
        else:
            return refresh_token

    def create(self, validated_data):
        refresh_token: RefreshToken = validated_data['refresh_token']

        if jwt_settings.ROTATE_REFRESH_TOKENS:
            if (
                    jwt_settings.BLACKLIST_AFTER_ROTATION
                    and 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS
            ):
                refresh_token.blacklist()

            # Update the refresh token with a new `jti`, `exp`, and `iat`.
            refresh_token.set_jti(), refresh_token.set_exp(), refresh_token.set_iat()

        return {
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token),
        }


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'email_verified',
            'avatar',
            'is_active',
            'first_name',
            'last_name',
            'date_joined'
        ]
        read_only_fields = [
            'id',
            'username',
            'avatar',
            'email',
            'email_verified',
            'is_active',
            'date_joined'
        ]
