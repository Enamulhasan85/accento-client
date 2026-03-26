from typing import Dict

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from bold_voice.identity.models import User


def generate_jwt_token_for_user(user: User) -> Dict[str, str]:
    token = RefreshToken.for_user(user=user)

    # Adding additional data to the token response
    token['email'] = user.email
    token['first_name'] = user.first_name
    token['last_name'] = user.last_name
    token['email_verified'] = user.email_verified
    token['is_active'] = user.is_active
    token['current_datetime'] = timezone.now().isoformat()

    token_data = {
        'refresh_token': str(token),
        'access_token': str(getattr(token, 'access_token')),
    }

    return token_data
