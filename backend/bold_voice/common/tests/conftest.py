import pytest

from bold_voice.common.tests.utils import login_client


@pytest.fixture
def user_with_all_permission(client):
    user = login_client(client)
    user.is_superuser = True
    user.save()
    return user
