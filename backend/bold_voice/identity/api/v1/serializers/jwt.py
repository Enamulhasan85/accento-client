from rest_framework import serializers


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    access_token = serializers.CharField(source='access')
    refresh_token = serializers.CharField(source='refresh')
