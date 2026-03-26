from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bold_voice.common.api.views import PostAPIView
from bold_voice.identity.api.v1.serializers import *
from bold_voice.identity.api.v1.serializers import UserInfoSerializer


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter


class RegisterAPIView(CreateAPIView):
    """API view to handle user registration requests."""
    permission_classes = []
    serializer_class = RegistrationSerializer


class LoginAPIView(PostAPIView):
    """API view to handle user login requests."""
    permission_classes = []
    serializer_class = LoginSerializer


class TokenRefreshAPIView(PostAPIView):
    """API view to handle token refresh requests."""
    permission_classes = []
    serializer_class = TokenRefreshSerializer


class EmailConfirmationAPIView(PostAPIView):
    """API view to handle email confirmation requests."""
    permission_classes = []
    serializer_class = EmailConfirmSerializer


class EmailConfirmationResendAPIView(PostAPIView):
    """API view to handle email confirmation resend requests."""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailConfirmationResendSerializer


class PasswordChangeAPIView(PostAPIView):
    """API view to handle password change requests."""
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer


class PasswordResetRequestAPIView(PostAPIView):
    """API view to handle password reset requests."""
    permission_classes = []
    serializer_class = PasswordResetRequestSerializer


class PasswordResetConfirmAPIView(PostAPIView):
    """API view to handle password reset confirmation requests."""
    permission_classes = []
    serializer_class = PasswordResetConfirmSerializer


class UserInfoAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get_object(self):
        return self.request.user


class UserDeleteAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # TODO(mazhar): Implement user deletion logic
        return Response(status=status.HTTP_204_NO_CONTENT)
