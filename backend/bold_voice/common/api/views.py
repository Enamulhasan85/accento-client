from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer


class PostAPIView(GenericAPIView):
    """
    A generic class for handling POST requests.
    Can be extended for more specific behaviors like creating or processing data.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_action(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # noinspection PyMethodMayBeStatic
    def perform_action(self, serializer: BaseSerializer):
        """
        This method can be overridden to define the specific action to be performed
        with the validated data (e.g., saving, processing, etc.).
        """
        serializer.save()
