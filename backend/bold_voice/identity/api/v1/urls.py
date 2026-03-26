from django.urls import path

from bold_voice.identity.api.v1.views import *

app_name = 'v1'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token-refresh/', TokenRefreshAPIView.as_view(), name='token-refresh'),
    path('email-confirm/', EmailConfirmationAPIView.as_view(), name='email-confirmation'),
    path('email-confirm/resend/', EmailConfirmationResendAPIView.as_view(), name='email-confirmation-resend'),
    path('password-change/', PasswordChangeAPIView.as_view(), name='password-change'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('delete/', UserDeleteAPIView.as_view(), name='delete'),
    path('me/', UserInfoAPIView.as_view(), name='user-info'),

    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('apple/login/', AppleLogin.as_view(), name='apple_login'),
]
