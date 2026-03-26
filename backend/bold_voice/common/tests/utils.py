import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from bold_voice.identity.tests.factories import UserFactory

User = get_user_model()


def convert_datetime_to_iso8601(datetime):
    """
    This function converts a datetime object to ISO 8601 formatted datetime

    :param datetime: Datetime object
    :return: ISO 8601 formatted datetime
    """
    return datetime.isoformat().replace("+00:00", "Z")


@pytest.mark.django_db
def create_factory_model_batch_for_attribute(factory_model, batch_size, attribute, values):
    """
    This function creates a batch of factory model instances with a specific attribute value

    :param factory_model: Factory model class of the instances to create
    :param batch_size: Number of instances to create
    :param attribute: Attribute name
    :param values: List of values for the attribute
    """
    for value in values:
        factory_model.create_batch(batch_size, **{attribute: value})


def login_client(client):
    Group.objects.get_or_create(name='Member')
    user = UserFactory(username='testuser', password='test_password')
    client.force_login(user)
    return user


def give_permission_to_user(user, obj, permissions):
    """
    Grants specified object-level permissions to a user by assigning the permission
    to the user based on the model and codename.
    Note: This does not create any new records or models; it assumes permissions exist.

    Args:
        user (User): The user to whom the permissions will be granted.
        obj (Model instance): The object for which the permissions are given.
        permissions (list): A list of permission codenames (e.g., ['change_exam', 'view_exam']).

    Returns:
        dict: A dictionary showing the permission and status (granted/failed).
    """
    results = {}
    for perm_codename in permissions:
        try:
            # Get the permission object
            perm = Permission.objects.get(codename=perm_codename, content_type__model=obj._meta.model_name)
            # Add permission to the user
            user.user_permissions.add(perm)
            results[perm_codename] = 'granted'
        except Permission.DoesNotExist:
            results[perm_codename] = 'failed: permission does not exist'
        except Exception as e:
            results[perm_codename] = f'failed: {str(e)}'

    return results
