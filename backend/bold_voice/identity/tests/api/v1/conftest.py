import pytest
from bold_voice.curriculum.models import Curriculum, Module
from bold_voice.curriculum.tests.api.factories import CurriculumConfigurationsFactory, CurriculumFactory, \
    ModuleFactory

from bold_voice.common.tests.utils import login_client


@pytest.fixture
def user(client):
    return login_client(client)


@pytest.fixture
def ielts_curriculum():
    curriculum = CurriculumFactory(name='IELTS', state=Curriculum.State.PUBLISHED)
    CurriculumConfigurationsFactory(curriculum=curriculum, min_score=4, max_score=9, pass_score=5)
    return curriculum


@pytest.fixture
def ielts_academic_module(ielts_curriculum):
    return ModuleFactory(
        name='Academic',
        code='ielts_academic',
        curriculum=ielts_curriculum,
        state=Module.State.PUBLISHED
    )


@pytest.fixture
def exam_profile(ielts_academic_module, user):
    return user.exam_profile
