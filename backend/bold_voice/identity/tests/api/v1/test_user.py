import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_get_user_info_authenticated(client, user):
    url = reverse('api:identity:v1:user-info')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user.id
    assert response.data['username'] == user.username
    assert response.data['email'] == user.email
    assert response.data['first_name'] == user.first_name
    assert response.data['last_name'] == user.last_name


@pytest.mark.django_db
def test_get_user_info_unauthenticated(client):
    url = reverse('api:identity:v1:user-info')
    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_user_registration_with_same_email_under_one_organization(client):
    url = reverse('api:identity:v1:register')
    payload = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'test@proxisprep.com',
        'password': 'Password@1234',
        'confirm_password': 'Password@1234'
    }
    Group.objects.create(name='Member')

    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access_token' in response.data
    assert 'refresh_token' in response.data

    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'email': ['User with the provided email already exists.']}


@pytest.mark.django_db
def test_user_registration_with_weak_password(client):
    url = reverse('api:identity:v1:register')
    payload = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'example@proxisprep.com',
        'password': 'password',
        'confirm_password': 'password'
    }

    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password': ['This password is too common.']}

    payload.update({
        'password': 'string',
        'confirm_password': 'string'
    })

    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password': ['This password is too short. It must contain at least 8 characters.']}


@pytest.mark.django_db
def test_create_user_with_valid_payload(client):
    url = reverse('api:identity:v1:register')
    payload = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john_doe@proxisprep.com',
        'password': 'Password@1234',
        'confirm_password': 'Password@1234'
    }
    Group.objects.create(name='Member')

    response = client.post(url, data=payload, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access_token' in response.data
    assert 'refresh_token' in response.data
