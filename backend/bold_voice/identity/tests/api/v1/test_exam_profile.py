import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from bold_voice.identity.models import ExamProfile

User = get_user_model()


@pytest.mark.django_db
def test_exam_profile_is_created_on_user_registration(client, ielts_academic_module, user):
    assert User.objects.count() == 1
    assert ExamProfile.objects.count() == 1


@pytest.mark.django_db
def test_exam_profile_scores_is_not_greater_than_curriculum_max_score(client, ielts_academic_module, user):
    url = reverse('api:identity:v1:exam-profile')
    payload = {
        'speaking_score': 10.0,
        'writing_score': 10.0,
        'listening_score': 10.0,
        'reading_score': 10.0,
    }

    response = client.patch(url, payload, content_type='application/json')
    expected_response = {
        'speaking_score': ['Speaking score cannot be greater than maximum score.'],
        'writing_score': ['Writing score cannot be greater than maximum score.'],
        'listening_score': ['Listening score cannot be greater than maximum score.'],
        'reading_score': ['Reading score cannot be greater than maximum score.']
    }

    assert response.status_code == 400
    assert response.data == expected_response


@pytest.mark.django_db
def test_exam_profile_exam_date_must_be_in_the_future(client, exam_profile):
    url = reverse('api:identity:v1:exam-profile')
    payload = {
        'exam_date': '2021-01-01',
    }

    response = client.patch(url, payload, content_type='application/json')
    expected_response = {
        'exam_date': ['Exam date must be a future date.']
    }

    assert response.status_code == 400
    assert response.data == expected_response
