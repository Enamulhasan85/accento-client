from rest_framework import serializers

from bold_voice.identity.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'email_verified',
            'is_active',
            'date_joined',
        ]
